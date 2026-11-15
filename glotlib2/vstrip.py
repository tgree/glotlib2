import threading

from OpenGL import GL


class VStrip:
    def __init__(self, plot, x1, x2, z=0, color=None, visible=True,
                 edge_color=None):
        self.plot       = plot
        self.x1         = x1
        self.x2         = x2
        self.data_x1    = None
        self.data_x2    = None
        self.z          = z
        self.color      = color
        self.edge_color = edge_color
        self.visible    = visible

        self.empty_vao = None

        self._vertices_lock = threading.Lock()

        self.plot.ctx._defer(self._init_gl)

    def _init_gl(self):
        self.empty_vao = GL.glGenVertexArrays(1)
        self.renormalize()

    def renormalize(self):
        '''
        Renormalizes the ertices to the current plot matrix.  Callable from any
        thread.
        '''
        self.data_x1 = (self.x1 * self.plot.rmatrix[0][0] +
                        self.plot.rmatrix[0][3])
        self.data_x2 = (self.x2 * self.plot.rmatrix[0][0] +
                        self.plot.rmatrix[0][3])

    def set_x_data(self, x1, x2):
        '''
        Moves the VStrip to the specified X coordinates.  Callable from any
        thread.
        '''
        self.x1 = x1
        self.x2 = x2
        self.renormalize()
        self.plot.ctx.mark_dirty()

    def show(self):
        self.visible = True
        self.plot.ctx.mark_dirty()

    def hide(self):
        self.visible = False
        self.plot.ctx.mark_dirty()

    def draw(self, z, mvp32, resolution):
        '''
        Renders the VStrip in the current GL context.  Must be called from a
        thread where the plot's ctx is the active GL context.
        '''
        if not self.visible:
            return

        GL.glEnable(GL.GL_BLEND)

        l = min(self.data_x1, self.data_x2)
        r = max(self.data_x1, self.data_x2)
        b = self.plot.mvpi[1][3] - self.plot.mvpi[1][1]
        t = self.plot.mvpi[1][3] + self.plot.mvpi[1][1]
        GL.glBindVertexArray(self.empty_vao)
        self.plot.ctx.programs.single_rect.use(
            l, t, r, b, z, mvp32, color=self.color)
        GL.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, 4)

        if self.edge_color is not None:
            w = self.plot.mvpi[0][0] * 2. / resolution[0]
            self.plot.ctx.programs.single_rect.use(
                l, t, l + w, b, z, mvp32, color=self.edge_color)
            GL.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, 4)

            self.plot.ctx.programs.single_rect.use(
                r - w, t, r, b, z, mvp32, color=self.edge_color)
            GL.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, 4)

        GL.glDisable(GL.GL_BLEND)
