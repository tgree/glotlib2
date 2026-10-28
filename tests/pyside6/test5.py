import sys

from PySide6.QtWidgets import QApplication

import glotlib2.pyside6


glotlib2.pyside6.init_backend()

app = QApplication(sys.argv)

w = glotlib2.pyside6.Window(900, 650, name='PySide6 Test 5')

p = w.ctx.add_plot(limits=(-100, -100, 100, 100))
p.add_hline(0, color=(0.5, 0.75, 0.5))
p.add_vline(0, color=(0.5, 0.75, 0.5))

w.show()

app.exec()
