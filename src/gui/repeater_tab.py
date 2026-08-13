from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QLineEdit, QCheckBox, QSplitter
)
from PyQt6.QtCore import Qt
from src.proxy.repeater_engine import send_request


class RepeaterTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        target_row = QHBoxLayout()
        target_row.addWidget(QLabel("Host:"))
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("example.com")
        target_row.addWidget(self.host_input)

        target_row.addWidget(QLabel("Port:"))
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("80")
        self.port_input.setFixedWidth(60)
        target_row.addWidget(self.port_input)

        self.https_checkbox = QCheckBox("HTTPS")
        target_row.addWidget(self.https_checkbox)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_clicked)
        target_row.addWidget(send_btn)

        layout.addLayout(target_row)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.request_box = QTextEdit()
        self.request_box.setPlaceholderText(
            "GET / HTTP/1.1\nHost: example.com\nUser-Agent: ShadowIntercepter\n\n"
        )
        splitter.addWidget(self.request_box)

        self.response_box = QTextEdit()
        self.response_box.setReadOnly(True)
        splitter.addWidget(self.response_box)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def send_clicked(self):
        host = self.host_input.text().strip()
        port_text = self.port_input.text().strip()
        use_https = self.https_checkbox.isChecked()

        if not host:
            self.response_box.setPlainText("[!] Host khaali nahi ho sakta")
            return

        port = int(port_text) if port_text else (443 if use_https else 80)
        raw_request = self.request_box.toPlainText()

        response = send_request(raw_request, host, port, use_https)
        self.response_box.setPlainText(response)

    def load_from_entry(self, req_dict):
        method = req_dict.get("method", "GET")
        path = req_dict.get("path", "/")
        version = req_dict.get("version", "HTTP/1.1")
        headers = req_dict.get("headers", {})
        body = req_dict.get("body", "")

        lines = [f"{method} {path} {version}"]
        for k, v in headers.items():
            lines.append(f"{k}: {v}")
        raw = "\r\n".join(lines) + "\r\n\r\n" + body

        self.request_box.setPlainText(raw)
        self.host_input.setText(req_dict.get("host", ""))
        self.port_input.setText(str(req_dict.get("port", 80)))
        self.https_checkbox.setChecked(req_dict.get("port") == 443)

    def load_raw(self, raw_text, host, port, is_https):
        self.request_box.setPlainText(raw_text)
        self.host_input.setText(host)
        self.port_input.setText(str(port))
        self.https_checkbox.setChecked(is_https)