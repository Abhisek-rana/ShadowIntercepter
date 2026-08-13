import threading


class InterceptManager:
    def __init__(self):
        self.request_intercept_enabled = False
        self.response_intercept_enabled = False

        self.pending_request = None
        self.pending_event = threading.Event()
        self.release_event = threading.Event()
        self.action = None
        self.modified_data = None

        self.pending_response = None
        self.response_pending_event = threading.Event()
        self.response_release_event = threading.Event()
        self.response_action = None
        self.response_modified_data = None

        self.lock = threading.Lock()

    def set_request_intercept(self, value: bool):
        self.request_intercept_enabled = value

    def is_request_intercept_enabled(self):
        return self.request_intercept_enabled

    def set_response_intercept(self, value: bool):
        self.response_intercept_enabled = value

    def is_response_intercept_enabled(self):
        return self.response_intercept_enabled

    def hold(self, raw_request_bytes: bytes, host: str, port: int, is_https: bool):
        with self.lock:
            self.pending_request = {
                "raw": raw_request_bytes.decode(errors="ignore"),
                "host": host,
                "port": port,
                "is_https": is_https,
            }
            self.release_event.clear()

        self.pending_event.set()
        self.release_event.wait()

        with self.lock:
            action = self.action
            final_data = self.modified_data
            self.pending_request = None
            self.pending_event.clear()

        if action == "forward":
            return "forward", final_data.encode()
        else:
            return "drop", None

    def get_pending(self):
        with self.lock:
            return self.pending_request

    def forward(self, edited_text: str):
        with self.lock:
            self.action = "forward"
            self.modified_data = edited_text
        self.release_event.set()

    def drop(self):
        with self.lock:
            self.action = "drop"
            self.modified_data = None
        self.release_event.set()

    def hold_response(self, raw_response_bytes: bytes, host: str, port: int):
        with self.lock:
            self.pending_response = {
                "raw": raw_response_bytes.decode(errors="ignore"),
                "host": host,
                "port": port,
            }
            self.response_release_event.clear()

        self.response_pending_event.set()
        self.response_release_event.wait()

        with self.lock:
            action = self.response_action
            final_data = self.response_modified_data
            self.pending_response = None
            self.response_pending_event.clear()

        if action == "forward":
            return "forward", final_data.encode()
        else:
            return "drop", None

    def get_pending_response(self):
        with self.lock:
            return self.pending_response

    def forward_response(self, edited_text: str):
        with self.lock:
            self.response_action = "forward"
            self.response_modified_data = edited_text
        self.response_release_event.set()

    def drop_response(self):
        with self.lock:
            self.response_action = "drop"
            self.response_modified_data = None
        self.response_release_event.set()


intercept_manager = InterceptManager()