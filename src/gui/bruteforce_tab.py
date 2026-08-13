import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QLineEdit, QComboBox, QCheckBox, QTableWidget,
    QTableWidgetItem, QSplitter
)
from PyQt6.QtCore import QTimer, Qt
from src.bruteforce.attack_engine import generate_requests
from src.proxy.repeater_engine import send_request


class BruteforceTab(QWidget):
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

        target_row.addWidget(QLabel("Attack type:"))
        self.attack_type_combo = QComboBox()
        self.attack_type_combo.addItems(
            ["Sniper", "Battering Ram", "Pitchfork", "Cluster Bomb"]
        )
        target_row.addWidget(self.attack_type_combo)

        layout.addLayout(target_row)

        top_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.template_box = QTextEdit()
        self.template_box.setPlaceholderText(
            "GET /login?user=§admin§&pass=§123§ HTTP/1.1\nHost: example.com\n\n"
            "(§...§ se ghero jo value badalni hai)"
        )
        top_splitter.addWidget(self.template_box)

        payload_widget = QWidget()
        payload_layout = QVBoxLayout()
        payload_layout.addWidget(QLabel("Payload Set 1 (ek line = ek payload):"))
        self.payload_box1 = QTextEdit()
        payload_layout.addWidget(self.payload_box1)

        payload_layout.addWidget(QLabel("Payload Set 2 (Pitchfork/Cluster Bomb ke liye):"))
        self.payload_box2 = QTextEdit()
        payload_layout.addWidget(self.payload_box2)
        payload_widget.setLayout(payload_layout)
        top_splitter.addWidget(payload_widget)

        layout.addWidget(top_splitter)

        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("Start Attack")
        self.start_btn.clicked.connect(self.start_attack)
        btn_row.addWidget(self.start_btn)

        self.status_label = QLabel("Ready")
        btn_row.addWidget(self.status_label)
        layout.addLayout(btn_row)

        bottom_splitter = QSplitter(Qt.Orientation.Vertical)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Payload(s)", "Status", "Length"])
        self.results_table.cellClicked.connect(self.show_response)
        bottom_splitter.addWidget(self.results_table)

        self.response_view = QTextEdit()
        self.response_view.setReadOnly(True)
        bottom_splitter.addWidget(self.response_view)

        layout.addWidget(bottom_splitter)
        self.setLayout(layout)

        self.results_data = []

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_table)
        self.timer.start(300)

    def start_attack(self):
        host = self.host_input.text().strip()
        port_text = self.port_input.text().strip()
        use_https = self.https_checkbox.isChecked()

        if not host:
            self.status_label.setText("[!] Host khaali nahi ho sakta")
            return

        port = int(port_text) if port_text else (443 if use_https else 80)
        template = self.template_box.toPlainText()

        payload_list1 = [
            line for line in self.payload_box1.toPlainText().split("\n") if line.strip()
        ]
        payload_list2 = [
            line for line in self.payload_box2.toPlainText().split("\n") if line.strip()
        ]

        attack_type_map = {
            "Sniper": "sniper",
            "Battering Ram": "battering_ram",
            "Pitchfork": "pitchfork",
            "Cluster Bomb": "cluster_bomb",
        }
        attack_type = attack_type_map[self.attack_type_combo.currentText()]

        if not payload_list1:
            self.status_label.setText("[!] Payload Set 1 khaali nahi ho sakta")
            return

        self.results_data = []
        self.results_table.setRowCount(0)
        self.start_btn.setEnabled(False)
        self.status_label.setText("Running...")

        thread = threading.Thread(
            target=self.run_attack,
            args=(template, attack_type, payload_list1, payload_list2, host, port, use_https),
        )
        thread.start()

    def run_attack(self, template, attack_type, payload_list1, payload_list2, host, port, use_https):
        try:
            requests_to_send = generate_requests(
                template, attack_type, payload_list1,
                payload_list2 if payload_list2 else None
            )
        except Exception as e:
            self.status_label.setText(f"[!] Template error: {e}")
            self.start_btn.setEnabled(True)
            return

        for payloads, raw_request in requests_to_send:
            fixed_request = raw_request.replace("\r\n", "\n").replace("\n", "\r\n")
            response = send_request(fixed_request, host, port, use_https)
            self.results_data.append((payloads, response))

        self.status_label.setText(f"Done — {len(requests_to_send)} requests sent")
        self.start_btn.setEnabled(True)

    def refresh_table(self):
        if self.results_table.rowCount() != len(self.results_data):
            self.results_table.setRowCount(len(self.results_data))
            for row, (payloads, response) in enumerate(self.results_data):
                status = "N/A"
                length = len(response)
                if response.startswith("HTTP/"):
                    try:
                        status = response.split(" ")[1]
                    except Exception:
                        pass

                self.results_table.setItem(row, 0, QTableWidgetItem(", ".join(payloads)))
                self.results_table.setItem(row, 1, QTableWidgetItem(status))
                self.results_table.setItem(row, 2, QTableWidgetItem(str(length)))

    def show_response(self, row, column):
        if row < len(self.results_data):
            _, response = self.results_data[row]
            self.response_view.setPlainText(response)

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

        self.template_box.setPlainText(raw)
        self.host_input.setText(req_dict.get("host", ""))
        self.port_input.setText(str(req_dict.get("port", 80)))
        self.https_checkbox.setChecked(req_dict.get("port") == 443)

    def load_raw(self, raw_text, host, port, is_https):
        self.template_box.setPlainText(raw_text)
        self.host_input.setText(host)
        self.port_input.setText(str(port))
        self.https_checkbox.setChecked(is_https)