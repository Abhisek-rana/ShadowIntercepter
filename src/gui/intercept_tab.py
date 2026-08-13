from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QCheckBox, QSplitter
)
from PyQt6.QtCore import QTimer, Qt
from src.intercept.intercept_manager import intercept_manager


class InterceptTab(QWidget):
    def __init__(self, repeater_tab=None, bruteforce_tab=None):
        super().__init__()
        self.repeater_tab = repeater_tab
        self.bruteforce_tab = bruteforce_tab

        layout = QVBoxLayout()

        top_row = QHBoxLayout()
        self.request_toggle = QCheckBox("Intercept Requests")
        self.request_toggle.stateChanged.connect(self.toggle_request_intercept)
        top_row.addWidget(self.request_toggle)

        self.response_toggle = QCheckBox("Intercept Responses")
        self.response_toggle.stateChanged.connect(self.toggle_response_intercept)
        top_row.addWidget(self.response_toggle)

        self.status_label = QLabel("Status: Waiting...")
        top_row.addWidget(self.status_label)

        layout.addLayout(top_row)

        splitter = QSplitter(Qt.Orientation.Vertical)

        req_widget = QWidget()
        req_layout = QVBoxLayout()
        req_layout.addWidget(QLabel("Request:"))

        self.request_box = QTextEdit()
        self.request_box.setPlaceholderText("Live request yahan dikhega...")
        req_layout.addWidget(self.request_box)

        req_btn_row = QHBoxLayout()
        req_forward_btn = QPushButton("Forward Request")
        req_forward_btn.clicked.connect(self.forward_request)
        req_btn_row.addWidget(req_forward_btn)

        req_drop_btn = QPushButton("Drop Request")
        req_drop_btn.clicked.connect(self.drop_request)
        req_btn_row.addWidget(req_drop_btn)

        req_repeater_btn = QPushButton("Send to Repeater")
        req_repeater_btn.clicked.connect(self.send_to_repeater)
        req_btn_row.addWidget(req_repeater_btn)

        req_brute_btn = QPushButton("Send to Bruteforce")
        req_brute_btn.clicked.connect(self.send_to_bruteforce)
        req_btn_row.addWidget(req_brute_btn)

        req_layout.addLayout(req_btn_row)
        req_widget.setLayout(req_layout)
        splitter.addWidget(req_widget)

        resp_widget = QWidget()
        resp_layout = QVBoxLayout()
        resp_layout.addWidget(QLabel("Response:"))

        self.response_box = QTextEdit()
        self.response_box.setPlaceholderText("Live response yahan dikhega...")
        resp_layout.addWidget(self.response_box)

        resp_btn_row = QHBoxLayout()
        resp_forward_btn = QPushButton("Forward Response")
        resp_forward_btn.clicked.connect(self.forward_response)
        resp_btn_row.addWidget(resp_forward_btn)

        resp_drop_btn = QPushButton("Drop Response")
        resp_drop_btn.clicked.connect(self.drop_response)
        resp_btn_row.addWidget(resp_drop_btn)

        resp_layout.addLayout(resp_btn_row)
        resp_widget.setLayout(resp_layout)
        splitter.addWidget(resp_widget)

        layout.addWidget(splitter)
        self.setLayout(layout)

        self.current_pending_request = None
        self.current_pending_response = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_pending)
        self.timer.start(300)

    def toggle_request_intercept(self, state):
        enabled = self.request_toggle.isChecked()
        intercept_manager.set_request_intercept(enabled)
        self.update_status()

    def toggle_response_intercept(self, state):
        enabled = self.response_toggle.isChecked()
        intercept_manager.set_response_intercept(enabled)
        self.update_status()

    def update_status(self):
        req_state = "ON" if intercept_manager.is_request_intercept_enabled() else "OFF"
        resp_state = "ON" if intercept_manager.is_response_intercept_enabled() else "OFF"
        self.status_label.setText(f"Status: Requests {req_state} | Responses {resp_state}")

    def check_pending(self):
        pending_req = intercept_manager.get_pending()
        if pending_req and pending_req != self.current_pending_request:
            self.current_pending_request = pending_req
            self.request_box.setPlainText(pending_req["raw"])
            self.status_label.setText(f"Status: Holding REQUEST to {pending_req['host']}:{pending_req['port']}")
        elif not pending_req and self.current_pending_request:
            self.current_pending_request = None

        pending_resp = intercept_manager.get_pending_response()
        if pending_resp and pending_resp != self.current_pending_response:
            self.current_pending_response = pending_resp
            self.response_box.setPlainText(pending_resp["raw"])
            self.status_label.setText(f"Status: Holding RESPONSE from {pending_resp['host']}:{pending_resp['port']}")
        elif not pending_resp and self.current_pending_response:
            self.current_pending_response = None

        if not pending_req and not pending_resp:
            self.update_status()

    def _fix_line_endings(self, text):
        return text.replace("\r\n", "\n").replace("\n", "\r\n")

    def forward_request(self):
        if not self.current_pending_request:
            return
        edited_text = self._fix_line_endings(self.request_box.toPlainText())
        intercept_manager.forward(edited_text)
        self.request_box.clear()
        self.current_pending_request = None

    def drop_request(self):
        if not self.current_pending_request:
            return
        intercept_manager.drop()
        self.request_box.clear()
        self.current_pending_request = None

    def send_to_repeater(self):
        if not self.current_pending_request or not self.repeater_tab:
            return
        raw_text = self.request_box.toPlainText()
        pending = self.current_pending_request
        self.repeater_tab.load_raw(raw_text, pending["host"], pending["port"], pending["is_https"])

    def send_to_bruteforce(self):
        if not self.current_pending_request or not self.bruteforce_tab:
            return
        raw_text = self.request_box.toPlainText()
        pending = self.current_pending_request
        self.bruteforce_tab.load_raw(raw_text, pending["host"], pending["port"], pending["is_https"])

    def _fix_chunked_encoding(self, text):
        if "\r\n\r\n" not in text:
            return text

        head, _, body = text.partition("\r\n\r\n")

        if "transfer-encoding: chunked" in head.lower():
            lines = body.split("\r\n")
            clean_body_parts = []
            skip_next = False
            for line in lines:
                if skip_next:
                    clean_body_parts.append(line)
                    skip_next = False
                    continue
                try:
                    int(line, 16)
                    skip_next = True
                    continue
                except ValueError:
                    if line != "":
                        clean_body_parts.append(line)

            clean_body = "".join(clean_body_parts)

            head_lines = [
                l for l in head.split("\r\n")
                if not l.lower().startswith("transfer-encoding:")
            ]
            head_lines.append(f"Content-Length: {len(clean_body.encode())}")
            new_head = "\r\n".join(head_lines)

            return new_head + "\r\n\r\n" + clean_body

        return text

    def forward_response(self):
        if not self.current_pending_response:
            return
        edited_text = self._fix_line_endings(self.response_box.toPlainText())
        edited_text = self._fix_chunked_encoding(edited_text)
        intercept_manager.forward_response(edited_text)
        self.response_box.clear()
        self.current_pending_response = None

    def drop_response(self):
        if not self.current_pending_response:
            return
        intercept_manager.drop_response()
        self.response_box.clear()
        self.current_pending_response = None