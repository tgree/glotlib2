import sys

from PySide6.QtWidgets import QApplication

import glotlib2.pyside6


glotlib2.pyside6.init_backend()

app = QApplication(sys.argv)

w = glotlib2.pyside6.Window(900, 650, name='Test 2')

w.ctx.add_label((0.5, 0.5),
                '.Woven silk pyjamas\nexchanged\nfor blue quartz.',
                face=w.ctx.faces.vera, font_size=20, font_oversample_log2=1,
                anchor='C')
w.show()

app.exec()
