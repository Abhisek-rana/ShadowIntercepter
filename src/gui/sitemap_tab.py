from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem
from src.sitemap.sitemap_builder import sitemap


class SiteMapTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_sitemap)
        layout.addWidget(refresh_btn)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Host / Path", "Method", "Status"])
        layout.addWidget(self.tree)

        self.setLayout(layout)
        self.load_sitemap()

    def load_sitemap(self):
        self.tree.clear()
        data = sitemap.build()

        for host, paths in data.items():
            host_item = QTreeWidgetItem([host])
            self.tree.addTopLevelItem(host_item)

            for path, info in paths.items():
                path_item = QTreeWidgetItem([path, info["method"], str(info["status"])])
                host_item.addChild(path_item)

        self.tree.expandAll()