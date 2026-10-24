from PySide6.QtWidgets import QWidget


class Window:
    def __init__(self, w, h, x=100, y=100, name=''):
        self.qt_window = QWidget()
        self.qt_window.setWindowTitle(name)
        self.qt_window.resize(w, h)
        self.qt_window.move(x, y)

    def show(self):
        self.qt_window.show()
