import sys
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
from PyQt6.QtGui import QIcon

from src.gui.dashboard_tab import DashboardTab
from src.gui.proxy_tab import ProxyTab
from src.gui.sitemap_tab import SiteMapTab
from src.gui.bruteforce_tab import BruteforceTab
from src.gui.repeater_tab import RepeaterTab
from src.gui.theme import DARK_GREEN_THEME
from src.proxy.tcp_proxy import start_proxy


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShadowIntercepter")
        self.setGeometry(100, 100, 1100, 700)
        self.setWindowIcon(QIcon("assets/icon.png"))

        self.repeater_tab = RepeaterTab()
        self.bruteforce_tab = BruteforceTab()

        tabs = QTabWidget()
        tabs.addTab(DashboardTab(), "Dashboard")
        tabs.addTab(ProxyTab(self.repeater_tab, self.bruteforce_tab), "Proxy")
        tabs.addTab(self.repeater_tab, "Repeater")
        tabs.addTab(SiteMapTab(), "Site Map")
        tabs.addTab(self.bruteforce_tab, "Bruteforce")

        self.setCentralWidget(tabs)


def run_gui():
    proxy_thread = threading.Thread(target=start_proxy, daemon=True)
    proxy_thread.start()

    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_GREEN_THEME)
    app.setWindowIcon(QIcon("assets/icon.png"))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()