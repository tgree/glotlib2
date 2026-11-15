import glotlib2.glfw
import glotlib2


class App(glotlib2.GLContextDelegate):
    def __init__(self):
        self.w = glotlib2.glfw.Window(512, 512, name='GLFW Test 10',
                                      delegate=self)

        self.label = self.w.ctx.add_label(
            (0.5, 0.5),
            '.Woven silk pyjamas\nexchanged\nfor blue quartz.',
            font=self.w.ctx.faces.vera(20, 1),
            anchor='C',
            )
        self.w.ctx.add_label((0.5, 0.5), '.', font=self.w.ctx.faces.vera(20, 1))

    def update_geometry(self):
        t = self.w.ctx.frame_time
        self.label.set_theta(t / 4)
        return True

    def start_animation(self):
        self.w.ctx.set_fps(60)


def main():
    glotlib2.glfw.init_backend()

    app = App()  # noqa: F841 # pylint: disable=unused-variable
    app.start_animation()

    glotlib2.glfw.interact()


if __name__ == '__main__':
    main()
