class HTTPRequest:
    def __init__(self, raw_data: bytes):
        self.raw_data = raw_data
        self.method = ""
        self.path = ""
        self.version = ""
        self.headers = {}
        self.body = b""
        self.host = ""
        self.port = 80
        self._parse()

    def _parse(self):
        try:
            head, _, self.body = self.raw_data.partition(b"\r\n\r\n")
            lines = head.decode(errors="ignore").split("\r\n")

            request_line = lines[0]
            self.method, self.path, self.version = request_line.split(" ")

            for line in lines[1:]:
                if ":" in line:
                    key, _, value = line.partition(":")
                    self.headers[key.strip()] = value.strip()

            host_header = self.headers.get("Host", "")
            if ":" in host_header:
                self.host, port_str = host_header.split(":")
                self.port = int(port_str)
            else:
                self.host = host_header
                self.port = 443 if self.path.startswith("https") else 80

        except Exception as e:
            print(f"[!] HTTP parse error: {e}")

    def to_dict(self):
        return {
            "method": self.method,
            "path": self.path,
            "version": self.version,
            "host": self.host,
            "port": self.port,
            "headers": self.headers,
            "body": self.body.decode(errors="ignore"),
        }

    def rebuild(self):
        lines = [f"{self.method} {self.path} {self.version}"]
        for key, value in self.headers.items():
            lines.append(f"{key}: {value}")
        head = "\r\n".join(lines).encode()
        return head + b"\r\n\r\n" + self.body


class HTTPResponse:
    def __init__(self, raw_data: bytes):
        self.raw_data = raw_data
        self.version = ""
        self.status_code = ""
        self.status_message = ""
        self.headers = {}
        self.body = b""
        self._parse()

    def _parse(self):
        try:
            head, _, self.body = self.raw_data.partition(b"\r\n\r\n")
            lines = head.decode(errors="ignore").split("\r\n")

            status_line = lines[0]
            parts = status_line.split(" ", 2)
            self.version = parts[0]
            self.status_code = parts[1]
            self.status_message = parts[2] if len(parts) > 2 else ""

            for line in lines[1:]:
                if ":" in line:
                    key, _, value = line.partition(":")
                    self.headers[key.strip()] = value.strip()

        except Exception as e:
            print(f"[!] HTTP response parse error: {e}")

    def to_dict(self):
        return {
            "status_code": self.status_code,
            "status_message": self.status_message,
            "headers": self.headers,
            "body": self.body.decode(errors="ignore"),
        }