import sys

from PySide6.QtWidgets import QApplication

import glotlib2.pyside6


glotlib2.pyside6.init_backend()

app = QApplication(sys.argv)

w = glotlib2.pyside6.Window(900, 650, name='Test 2')

p = w.ctx.add_plot(limits=(-100, -100, 100, 100))
p.set_x_label('X axis')
p.set_y_label('Y axis')

w.show()
print(p.x_label.mvp)
print('%s x %s' % (p.x_label.width, p.x_label.height))
print('(%s, %s)' % p.x_label.pos)

app.exec()
