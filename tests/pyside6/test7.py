import sys
import math

import numpy as np
from PySide6.QtWidgets import QApplication

import glotlib2.pyside6
import glotlib2


NVERTICES = 501


class App(glotlib2.GLContextDelegate):
    def __init__(self):
        self.w = glotlib2.pyside6.Window(900, 650, name='PySide6 Test 7',
                                         delegate=self)

        self.plot = self.w.ctx.add_plot(limits=(0, -1, math.pi * 2, 1))
        X = np.linspace(0, math.pi * 2, NVERTICES)
        Y = np.sin(X)
        self.plot.add_steps(X=X, Y=Y)
        self.plot.set_x_label('X label goes here')

        self.w.show()

        self.plot.set_y_label('Y label goes here')


def main():
    glotlib2.pyside6.init_backend()
    q_app = QApplication(sys.argv)
    app = App()  # noqa: F841 # pylint: disable=unused-variable
    q_app.exec()


if __name__ == '__main__':
    main()
