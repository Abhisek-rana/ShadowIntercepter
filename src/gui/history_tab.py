from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QTextEdit, QHBoxLayout, QSplitter, QLabel
)
from PyQt6.QtCore import Qt
from src.history.history_store import history


class HistoryTab(QWidget):
    def __init__(self, repeater_tab=None, bruteforce_tab=None):
        super().__init__()
        self.repeater_tab = repeater_tab
        self.bruteforce_tab = bruteforce_tab

        layout = QVBoxLayout()

        top_row = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_history)
        top_row.addWidget(refresh_btn)

        send_btn = QPushButton("Send to Repeater")
        send_btn.clicked.connect(self.send_to_repeater)
        top_row.addWidget(send_btn)

        brute_btn = QPushButton("Send to Bruteforce")
        brute_btn.clicked.connect(self.send_to_bruteforce)
        top_row.addWidget(brute_btn)

        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self.clear_history)
        top_row.addWidget(clear_btn)

        layout.addLayout(top_row)

        splitter = QSplitter(Qt.Orientation.Vertical)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Method", "Host", "Path", "Status"])
        self.table.cellClicked.connect(self.show_detail)
        splitter.addWidget(self.table)

        detail_splitter = QSplitter(Qt.Orientation.Horizontal)

        req_widget = QWidget()
        req_layout = QVBoxLayout()
        req_layout.addWidget(QLabel("Request:"))
        self.request_view = QTextEdit()
        req_layout.addWidget(self.request_view)
        req_widget.setLayout(req_layout)
        detail_splitter.addWidget(req_widget)

        resp_widget = QWidget()
        resp_layout = QVBoxLayout()
        resp_layout.addWidget(QLabel("Response:"))
        self.response_view = QTextEdit()
        resp_layout.addWidget(self.response_view)
        resp_widget.setLayout(resp_layout)
        detail_splitter.addWidget(resp_widget)

        splitter.addWidget(detail_splitter)
        layout.addWidget(splitter)
        self.setLayout(layout)

        self.selected_row = None
        self.load_history()

    def load_history(self):
        entries = history.get_all()
        self.table.setRowCount(len(entries))

        for row, entry in enumerate(entries):
            req = entry["request"]
            resp = entry.get("response") or {}

            self.table.setItem(row, 0, QTableWidgetItem(str(entry["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(req.get("method", "")))
            self.table.setItem(row, 2, QTableWidgetItem(req.get("host", "")))
            self.table.setItem(row, 3, QTableWidgetItem(req.get("path", "")))
            self.table.setItem(row, 4, QTableWidgetItem(str(resp.get("status_code", "N/A"))))

    def show_detail(self, row, column):
        self.selected_row = row
        entry_id = int(self.table.item(row, 0).text())
        entry = history.get_by_id(entry_id)
        if not entry:
            return

        req = entry["request"]
        resp = entry.get("response") or {}

        req_text = f"{req.get('method')} {req.get('path')} {req.get('version')}\n"
        for k, v in req.get("headers", {}).items():
            req_text += f"{k}: {v}\n"
        if req.get("body"):
            req_text += f"\n{req.get('body')}\n"
        self.request_view.setPlainText(req_text)

        resp_text = f"Status: {resp.get('status_code')} {resp.get('status_message')}\n"
        for k, v in resp.get("headers", {}).items():
            resp_text += f"{k}: {v}\n"
        if resp.get("body"):
            resp_text += f"\n{resp.get('body')[:2000]}\n"
        self.response_view.setPlainText(resp_text)

    def send_to_repeater(self):
        if self.selected_row is None:
            self.request_view.setPlainText("[!] Pehle ek row select karo table mein")
            return

        entry_id = int(self.table.item(self.selected_row, 0).text())
        entry = history.get_by_id(entry_id)
        if not entry or not self.repeater_tab:
            return

        self.repeater_tab.load_from_entry(entry["request"])

    def send_to_bruteforce(self):
        if self.selected_row is None:
            self.request_view.setPlainText("[!] Pehle ek row select karo table mein")
            return

        entry_id = int(self.table.item(self.selected_row, 0).text())
        entry = history.get_by_id(entry_id)
        if not entry or not self.bruteforce_tab:
            return

        self.bruteforce_tab.load_from_entry(entry["request"])

    def clear_history(self):
        history.clear()
        self.table.setRowCount(0)
        self.request_view.clear()
        self.response_view.clear()
        self.selected_row = None