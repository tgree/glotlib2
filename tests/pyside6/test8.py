import sys
import math

import numpy as np
from PySide6.QtWidgets import QApplication

import glotlib2.pyside6
import glotlib2


NPOINTS = 5000000


class App(glotlib2.GLContextDelegate):
    def __init__(self):
        self.w = glotlib2.pyside6.Window(512, 512, name='PySide6 Test 8',
                                         delegate=self)

        self.plot = self.w.ctx.add_plot(limits=(-6, -6, 6, 6))
        X = np.random.normal(0, 1, NPOINTS)
        Y = np.random.normal(0, 1, NPOINTS)
        self.plot.add_points(X=X, Y=Y)

        self.w.show()


def main():
    glotlib2.pyside6.init_backend()
    q_app = QApplication(sys.argv)
    app = App()  # noqa: F841 # pylint: disable=unused-variable
    q_app.exec()


if __name__ == '__main__':
    main()
