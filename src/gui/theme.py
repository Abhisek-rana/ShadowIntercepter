DARK_GREEN_THEME = """
QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: 'Segoe UI', 'Ubuntu', sans-serif;
    font-size: 13px;
    border: none;
}

QMainWindow {
    background-color: #0d1117;
}

QTabWidget::pane {
    border: none;
    background-color: #0d1117;
    border-top: 1px solid #21262d;
    top: -1px;
}

QTabBar {
    background-color: transparent;
}

QTabBar::tab {
    background-color: transparent;
    color: #8b949e;
    padding: 10px 20px;
    margin-right: 2px;
    border: none;
    border-bottom: 2px solid transparent;
}

QTabBar::tab:selected {
    color: #39ff82;
    border-bottom: 2px solid #39ff82;
    font-weight: bold;
}

QTabBar::tab:hover {
    color: #39ff82;
}

QPushButton {
    background-color: #14261c;
    color: #39ff82;
    border: 1px solid #234433;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #39ff82;
    color: #0d1117;
    border: 1px solid #39ff82;
}

QPushButton:pressed {
    background-color: #2ecc71;
    color: #0d1117;
}

QPushButton:disabled {
    background-color: #12161c;
    color: #484f58;
    border: 1px solid #1c2128;
}

QLineEdit, QTextEdit, QComboBox {
    background-color: #12161c;
    color: #c9d1d9;
    border: 1px solid #21262d;
    border-radius: 6px;
    padding: 6px 8px;
    selection-background-color: #39ff82;
    selection-color: #0d1117;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 1px solid #39ff82;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #12161c;
    color: #c9d1d9;
    selection-background-color: #14261c;
    selection-color: #39ff82;
    border: 1px solid #21262d;
    border-radius: 6px;
}

QTableWidget, QTreeWidget {
    background-color: #0d1117;
    alternate-background-color: #12161c;
    color: #c9d1d9;
    gridline-color: #1c2128;
    border: 1px solid #1c2128;
    border-radius: 8px;
}

QHeaderView::section {
    background-color: #12161c;
    color: #39ff82;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #21262d;
    font-weight: bold;
}

QTableWidget::item, QTreeWidget::item {
    padding: 4px;
    border: none;
}

QTableWidget::item:selected, QTreeWidget::item:selected {
    background-color: #14261c;
    color: #39ff82;
    border-radius: 4px;
}

QCheckBox {
    color: #c9d1d9;
    spacing: 10px;
    padding: 4px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #39ff82;
    border-radius: 4px;
    background-color: #12161c;
}

QCheckBox::indicator:checked {
    background-color: #39ff82;
}

QLabel {
    color: #c9d1d9;
    background-color: transparent;
    padding: 2px 0px;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px;
}

QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 2px;
}

QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #21262d;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
    background: #39ff82;
}

QScrollBar::add-line, QScrollBar::sub-line {
    border: none;
    background: none;
    height: 0px;
    width: 0px;
}

QSplitter::handle {
    background-color: #12161c;
}

QSplitter::handle:hover {
    background-color: #39ff82;
}

QSplitter::handle:horizontal {
    width: 4px;
}

QSplitter::handle:vertical {
    height: 4px;
}
"""
