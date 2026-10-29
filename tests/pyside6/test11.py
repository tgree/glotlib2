import sys
import math

import numpy as np
from PySide6.QtWidgets import QApplication

import glotlib2.pyside6
import glotlib2


NVERTICES = 501


class App(glotlib2.GLContextDelegate):
    def __init__(self):
        self.w = glotlib2.pyside6.Window(900, 650, name='PySide6 Test 11',
                                         delegate=self)

        self.plot = self.w.ctx.add_plot(limits=(0, -1, math.pi * 2, 1))
        X = np.linspace(0, math.pi * 2, NVERTICES)
        Y = np.sin(X)
        self.lines = self.plot.add_lines(X=X, Y=Y)
        self.plot.set_x_label('X label goes here')

        self.half_X = X[NVERTICES // 4: 3 * NVERTICES // 4]
        self.half_Y = Y[NVERTICES // 4: 3 * NVERTICES // 4]

        self.w.show()

        self.plot.set_y_label('Y label goes here')

        self.moves = 0

    def handle_mouse_moved(self, _plot, _x, _y):
        self.moves += 1
        if self.moves == 100:
            self.moves = 0
            self.half_Y = -self.half_Y
            self.lines.sub_x_y_data(NVERTICES // 4, self.half_X, self.half_Y)


def main():
    glotlib2.pyside6.init_backend()
    q_app = QApplication(sys.argv)
    app = App()  # noqa: F841 # pylint: disable=unused-variable
    q_app.exec()


if __name__ == '__main__':
    main()
