import sys

from PySide6.QtWidgets import QApplication

import glotlib2.pyside6


glotlib2.pyside6.init_backend()

app = QApplication(sys.argv)

w = glotlib2.pyside6.Window(900, 650, name='Test 2')

w.ctx.add_plot(limits=(-100, -100, 100, 100))

w.show()

app.exec()
