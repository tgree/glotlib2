from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import QCoreApplication

from .gl_context import GLContext
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

        self.ctx = GLContext(self.gl_widget, msaa=msaa)

    def show(self):
        # This line fixes the issue where the window seems to "expand into
        # place" when first rendered, but I'm not sure how safe it is in a
        # complex app:
        # QCoreApplication.processEvents()
        self.qt_window.show()
