import sys
import math

import numpy as np

import glotlib2.glfw
import glotlib2


NVERTICES = 501


class App(glotlib2.GLContextDelegate):
    def __init__(self):
        self.w = glotlib2.glfw.Window(900, 650, name='GLFW Test 6',
                                      delegate=self)

        self.plot = self.w.ctx.add_plot(limits=(0, -1, math.pi * 2, 1))
        X = np.linspace(0, math.pi * 2, NVERTICES)
        Y = np.sin(X)
        self.plot.add_steps(X=X, Y=Y)
        self.plot.set_x_label('X label goes here')
        self.plot.set_y_label('Y label goes here')


def main():
    glotlib2.glfw.init_backend()
    app = App()  # noqa: F841 # pylint: disable=unused-variable
    glotlib2.glfw.interact()


if __name__ == '__main__':
    main()
