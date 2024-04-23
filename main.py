import sys

from PyQt6.QtWidgets import QApplication

from gui.MainWindow import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open('gui/styles.qss', 'r', encoding="utf-8") as f:
        style = f.read()
        app.setStyleSheet(style)

    window = MainWindow()
    window.show()
    app.exec()
