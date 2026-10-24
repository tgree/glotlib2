from PySide6.QtWidgets import QWidget, QHBoxLayout

from .gl_widget import GLWidget


class Window:
    def __init__(self, w, h, x=100, y=100, name='', msaa=None):
        self.qt_window = QWidget()
        self.qt_window.setWindowTitle(name)
        self.qt_window.resize(w, h)
        self.qt_window.move(x, y)

        layout = QHBoxLayout(self.qt_window)
        self.gl_widget = GLWidget(self, msaa, parent=self.qt_window)
        layout.addWidget(self.gl_widget)

    def show(self):
        self.qt_window.show()
