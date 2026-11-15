import sys
import math

import numpy as np
from PySide6.QtWidgets import QApplication

import glotlib2.pyside6
import glotlib2


NVERTICES = 501


class App(glotlib2.GLContextDelegate):
    def __init__(self):
        self.w = glotlib2.pyside6.Window(900, 650, name='PySide6 Test 15',
                                         delegate=self)

        X = np.linspace(0, math.pi * 2, NVERTICES)
        Y = np.sin(X)

        p1 = self.w.ctx.add_plot(211, limits=(0, -1, math.pi * 2, 1))
        p1.add_vstrip(2, 1, color=(0.5, 0.75, 0.5, 0.25),
                      edge_color=(0.5, 0.75, 0.5, 1))
        p1.add_steps(X=X, Y=Y)
        p2 = self.w.ctx.add_plot(212, limits=(0, -1, math.pi * 2, 1),
                                 sharex=p1.x_axis, sharey=p1.y_axis)
        p2.add_steps(X=X, Y=Y)

        self.w.show()


def main():
    glotlib2.pyside6.init_backend()
    q_app = QApplication(sys.argv)
    app = App()  # noqa: F841 # pylint: disable=unused-variable
    q_app.exec()


if __name__ == '__main__':
    main()
