import socket
import ssl


def send_request(raw_request: str, host: str, port: int, use_https: bool = False, timeout=10):
    """
    Raw request (string) ko diye gaye host:port par bhejta hai.
    HTTP ya HTTPS dono support karta hai.
    """
    try:
        raw_bytes = raw_request.encode()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))

        if use_https:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            sock = context.wrap_socket(sock, server_hostname=host)

        sock.send(raw_bytes)

        response = b""
        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            except socket.timeout:
                break

        sock.close()
        return response.decode(errors="ignore")

    except Exception as e:
        return f"[!] Error: {e}"