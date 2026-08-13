from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer
from src.history.history_store import history
from src.intercept.intercept_manager import intercept_manager


class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("ShadowIntercepter Dashboard")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.status_label = QLabel("Proxy Status: Running on 127.0.0.1:8080")
        layout.addWidget(self.status_label)

        self.intercept_label = QLabel("Intercept: OFF")
        layout.addWidget(self.intercept_label)

        self.requests_label = QLabel("Total Requests Captured: 0")
        layout.addWidget(self.requests_label)

        layout.addStretch()
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_stats)
        self.timer.start(1000)

    def refresh_stats(self):
        req_state = "ON" if intercept_manager.is_request_intercept_enabled() else "OFF"
        resp_state = "ON" if intercept_manager.is_response_intercept_enabled() else "OFF"
        self.intercept_label.setText(f"Intercept: Requests {req_state} | Responses {resp_state}")
        self.requests_label.setText(
            f"Total Requests Captured: {len(history.get_all())}"
        )