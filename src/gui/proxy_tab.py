from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from src.gui.intercept_tab import InterceptTab
from src.gui.history_tab import HistoryTab


class ProxyTab(QWidget):
    def __init__(self, repeater_tab=None, bruteforce_tab=None):
        super().__init__()

        layout = QVBoxLayout()

        sub_tabs = QTabWidget()
        sub_tabs.addTab(InterceptTab(repeater_tab, bruteforce_tab), "Intercept")
        sub_tabs.addTab(HistoryTab(repeater_tab, bruteforce_tab), "HTTP History")

        layout.addWidget(sub_tabs)
        self.setLayout(layout)