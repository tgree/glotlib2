import sys
import math

import numpy as np

import glotlib2.glfw
import glotlib2


NPOINTS = 5000000


class App(glotlib2.GLContextDelegate):
    def __init__(self):
        self.w = glotlib2.glfw.Window(512, 512, name='GLFW Test 7',
                                      delegate=self)

        self.plot = self.w.ctx.add_plot(limits=(-6, -6, 6, 6))
        X = np.random.normal(0, 1, NPOINTS)
        Y = np.random.normal(0, 1, NPOINTS)
        self.plot.add_points(X=X, Y=Y)


def main():
    glotlib2.glfw.init_backend()
    app = App()  # noqa: F841 # pylint: disable=unused-variable
    glotlib2.glfw.interact()


if __name__ == '__main__':
    main()
