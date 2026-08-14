import socket
import ssl
import threading
from src.proxy.http_parser import HTTPRequest, HTTPResponse
from src.history.history_store import history
from src.proxy.ssl_handler import ensure_ca, get_cert_for_domain, CA_CERT_FILE, CA_KEY_FILE
from src.intercept.intercept_manager import intercept_manager


def recv_full_response(sock, idle_timeout=2):
    sock.settimeout(idle_timeout)
    data = b""
    try:
        while True:
            chunk = sock.recv(8192)
            if not chunk:
                break
            data += chunk
    except socket.timeout:
        pass
    return data


def force_connection_close(raw_bytes):
    try:
        text = raw_bytes.decode(errors="ignore")
        head, sep, body = text.partition("\r\n\r\n")
        lines = head.split("\r\n")

        found = False
        new_lines = []
        for line in lines:
            if line.lower().startswith("connection:"):
                new_lines.append("Connection: close")
                found = True
            else:
                new_lines.append(line)

        if not found:
            new_lines.append("Connection: close")

        new_head = "\r\n".join(new_lines)
        return (new_head + sep + body).encode()
    except Exception:
        return raw_bytes


def force_no_compression(raw_bytes):
    """
    'Accept-Encoding' header ko 'identity' bana deta hai — server se
    uncompressed response maangta hai, taaki hamara text-based processing
    (decode/encode) response ko corrupt na kare.
    """
    try:
        text = raw_bytes.decode(errors="ignore")
        head, sep, body = text.partition("\r\n\r\n")
        lines = head.split("\r\n")

        new_lines = []
        for line in lines:
            if line.lower().startswith("accept-encoding:"):
                new_lines.append("Accept-Encoding: identity")
            else:
                new_lines.append(line)

        new_head = "\r\n".join(new_lines)
        return (new_head + sep + body).encode()
    except Exception:
        return raw_bytes


SKIP_EXTENSIONS = (
    ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".woff", ".woff2", ".ttf", ".eot", ".map", ".webp", ".mp4", ".mp3",
    ".avif", ".bmp",
)


def should_skip_intercept(path):
    clean_path = path.split("?")[0].lower()
    return clean_path.endswith(SKIP_EXTENSIONS)


def relay(src_socket, dst_socket):
    try:
        while True:
            data = src_socket.recv(4096)
            if not data:
                break
            dst_socket.send(data)
    except Exception:
        pass
    finally:
        try:
            src_socket.close()
        except Exception:
            pass
        try:
            dst_socket.close()
        except Exception:
            pass


def handle_https_connect(client_socket, target_host, target_port):
    client_socket.send(b"HTTP/1.1 200 Connection Established\r\n\r\n")

    cert_path, key_path = get_cert_for_domain(target_host)

    try:
        client_ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        client_ssl_context.load_cert_chain(certfile=cert_path, keyfile=key_path)
        client_ssl_socket = client_ssl_context.wrap_socket(client_socket, server_side=True)
    except Exception as e:
        print(f"[!] Client SSL handshake failed for {target_host}: {e}")
        client_socket.close()
        return

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((target_host, target_port))
        server_ssl_context = ssl.create_default_context()
        server_ssl_context.check_hostname = False
        server_ssl_context.verify_mode = ssl.CERT_NONE
        server_ssl_socket = server_ssl_context.wrap_socket(server_socket, server_hostname=target_host)
    except Exception as e:
        print(f"[!] Could not connect to real server {target_host}: {e}")
        client_ssl_socket.close()
        return

    try:
        request_data = client_ssl_socket.recv(4096)
        if request_data:
            req = HTTPRequest(request_data)
            req.host = target_host
            req.port = target_port

            final_request_bytes = force_no_compression(force_connection_close(request_data))
            skip = should_skip_intercept(req.path)

            if intercept_manager.is_request_intercept_enabled() and not skip:
                print(f"[INTERCEPT] Holding HTTPS request: {req.method} https://{target_host}{req.path}")
                action, modified_bytes = intercept_manager.hold(
                    final_request_bytes, target_host, target_port, is_https=True
                )
                if action == "drop":
                    print("[INTERCEPT] HTTPS request dropped by user.")
                    client_ssl_socket.close()
                    server_ssl_socket.close()
                    return
                else:
                    final_request_bytes = modified_bytes
                    req = HTTPRequest(final_request_bytes)
                    req.host = target_host
                    req.port = target_port

            print(f"[HTTPS INTERCEPTED] {req.method} https://{target_host}{req.path}")

            server_ssl_socket.send(final_request_bytes)
            response_data = recv_full_response(server_ssl_socket)
            response_data = force_connection_close(response_data)

            if intercept_manager.is_response_intercept_enabled() and not skip:
                print(f"[INTERCEPT] Holding HTTPS response from {target_host}")
                action, modified_response = intercept_manager.hold_response(
                    response_data, target_host, target_port
                )
                if action == "drop":
                    print("[INTERCEPT] HTTPS response dropped by user.")
                    response_data = b""
                else:
                    response_data = modified_response

            client_ssl_socket.send(response_data)

            resp_dict = None
            if response_data:
                resp = HTTPResponse(response_data)
                resp_dict = resp.to_dict()
            history.add_entry(req.to_dict(), resp_dict)
    except Exception as e:
        print(f"[!] HTTPS relay error: {e}")
    finally:
        try:
            client_ssl_socket.close()
        except Exception:
            pass
        try:
            server_ssl_socket.close()
        except Exception:
            pass


def handle_client(client_socket):
    request_data = client_socket.recv(4096)
    if not request_data:
        client_socket.close()
        return

    if request_data.startswith(b"CONNECT"):
        first_line = request_data.decode(errors="ignore").split("\r\n")[0]
        target = first_line.split(" ")[1]
        target_host, target_port = target.split(":")
        handle_https_connect(client_socket, target_host, int(target_port))
        return

    req = HTTPRequest(request_data)
    if not req.host:
        client_socket.close()
        return

    final_request_bytes = force_no_compression(force_connection_close(req.rebuild()))
    skip = should_skip_intercept(req.path)

    if intercept_manager.is_request_intercept_enabled() and not skip:
        print(f"[INTERCEPT] Holding request: {req.method} {req.host}{req.path}")
        action, modified_bytes = intercept_manager.hold(
            final_request_bytes, req.host, req.port, is_https=False
        )
        if action == "drop":
            print("[INTERCEPT] Request dropped by user.")
            client_socket.close()
            return
        else:
            final_request_bytes = modified_bytes
            req = HTTPRequest(final_request_bytes)

    print(f"[INTERCEPTED] {req.method} {req.host}:{req.port}{req.path}")

    response_data = b""
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((req.host, req.port))
        server_socket.send(final_request_bytes)

        response_data = recv_full_response(server_socket)
        response_data = force_connection_close(response_data)

        if intercept_manager.is_response_intercept_enabled() and not skip:
            print(f"[INTERCEPT] Holding response from {req.host}")
            action, modified_response = intercept_manager.hold_response(
                response_data, req.host, req.port
            )
            if action == "drop":
                print("[INTERCEPT] Response dropped by user.")
                response_data = b""
            else:
                response_data = modified_response

        client_socket.send(response_data)
        server_socket.close()
    except Exception as e:
        print(f"[!] Error connecting to target: {e}")
    finally:
        client_socket.close()

    resp_dict = None
    if response_data:
        resp = HTTPResponse(response_data)
        resp_dict = resp.to_dict()

    history.add_entry(req.to_dict(), resp_dict)


def start_proxy(listen_host="127.0.0.1", listen_port=8080):
    ensure_ca()

    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_socket.bind((listen_host, listen_port))
    proxy_socket.listen(5)
    print(f"[+] Proxy listening on {listen_host}:{listen_port}")

    while True:
        client_socket, addr = proxy_socket.accept()
        print(f"[+] Connection from {addr}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()


if __name__ == "__main__":
    start_proxy()