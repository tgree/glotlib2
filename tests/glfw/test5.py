import glotlib2.glfw
import glotlib2


class App(glotlib2.GLContextDelegate):
    def __init__(self):
        self.w = glotlib2.glfw.Window(900, 650, name='GLFW Test 5',
                                      delegate=self)

        self.plot  = self.w.ctx.add_plot(limits=(-100, -100, 100, 100))
        self.hline = self.plot.add_hline(0, color=(0.5, 0.75, 0.5))
        self.vline = self.plot.add_vline(0, color=(0.5, 0.75, 0.5))

    def handle_mouse_moved(self, plot, x, y):
        if plot == self.plot:
            x, y = self.plot._context_to_data(x, y)
            self.hline.set_y_data(y)
            self.vline.set_x_data(x)


def main():
    glotlib2.glfw.init_backend()
    app = App()
    glotlib2.glfw.interact()


if __name__ == '__main__':
    main()
