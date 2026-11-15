import sys

from PySide6.QtWidgets import QApplication

import glotlib2.pyside6


glotlib2.pyside6.init_backend()

app = QApplication(sys.argv)

w = glotlib2.pyside6.Window(900, 650, name='PySide6 Test 2')
w.show()

w.ctx.add_label((0.5, 0.5),
                '.Woven silk pyjamas\nexchanged\nfor blue quartz.',
                font=w.ctx.faces.vera(20, 1), anchor='C')

app.exec()
