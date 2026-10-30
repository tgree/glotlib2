import sys

from PySide6.QtWidgets import QApplication

import glotlib2.pyside6
import glotlib2


NVERTICES = 501


class App(glotlib2.GLContextDelegate):
    def __init__(self):
        self.w = glotlib2.pyside6.Window(512, 512, name='PySide6 Test 12',
                                         delegate=self)

        self.label = self.w.ctx.add_label(
            (0.5, 0.5),
            '.Woven silk pyjamas\nexchanged\nfor blue quartz.',
            font=self.w.ctx.faces.vera(20, 1),
            anchor='C',
            )
        self.w.ctx.add_label((0.5, 0.5), '.', font=self.w.ctx.faces.vera(20, 1))

        self.w.show()

    def update_geometry(self):
        t = self.w.ctx.frame_time
        self.label.set_theta(t / 4)
        return True

    def start_animation(self):
        self.w.ctx.set_fps(60)


def main():
    glotlib2.pyside6.init_backend()

    q_app = QApplication(sys.argv)

    app = App()  # noqa: F841 # pylint: disable=unused-variable
    app.start_animation()

    q_app.exec()


if __name__ == '__main__':
    main()
