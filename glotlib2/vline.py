import numpy as np
from OpenGL import GL

from . import vbo


INSTANCE_GEOMETRY = np.array(
    [[0, -0.5],
     [1, -0.5],
     [1,  0.5],
     [0, -0.5],
     [1,  0.5],
     [0,  0.5],
     ], dtype=np.float32)


class VLine:
    def __init__(self, plot, x, color=None, width=1, visible=True):
        self.plot     = plot
        self.x        = x
        self.color    = color
        self.width    = width
        self.visible  = visible
        self.vertices = [(x, -1), (x, 1)]

        self.line_vao = None
        self.vert_vbo = vbo.VBO(plot.ctx, self.vertices)
        self.geom_vbo = vbo.StaticVBO(plot.ctx, INSTANCE_GEOMETRY)

        self.plot.ctx._defer(self._init_gl)

    def _init_gl(self):
        self.line_vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.line_vao)

        self.vert_vbo._init_gl()
        self.vert_vbo._attrib_pointer(0)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribDivisor(0, 1)

        self.vert_vbo._attrib_pointer(1, 8)
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribDivisor(1, 1)

        self.geom_vbo._init_gl()
        self.geom_vbo._attrib_pointer(2)
        GL.glEnableVertexAttribArray(2)
        GL.glVertexAttribDivisor(2, 0)

        GL.glBindVertexArray(0)

        self.renormalize()

    def renormalize(self):
        '''
        Renormalizes the VBO vertices to the current plot matrix.  Callable
        from any thread.
        '''
        x = self.x * self.plot.rmatrix[0][0] + self.plot.rmatrix[0][3]
        self.vert_vbo.set_x_data(x)

    def set_x_data(self, x):
        '''
        Moves the VLine to the specified X coordinate.  Callable from any
        thread.
        '''
        self.x = x
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
        Renders the VLine in the current GL context.  Must be called from a
        thread where the plot's ctx is the active GL context.
        '''
        if not self.width or not self.visible:
            return

        # This is distasteful.  We need to get notifications for changes to
        # plot.mvpi and then do this via a vert_vbo.sub_y_data() call instead.
        b = self.plot.mvpi[1][3] - self.plot.mvpi[1][1]
        t = self.plot.mvpi[1][3] + self.plot.mvpi[1][1]
        self.vert_vbo.vertices[0][1] = b
        self.vert_vbo.vertices[1][1] = t
        self.vert_vbo._sub_vbo_range(0, 2, self.vert_vbo.vertices)

        GL.glBindVertexArray(self.line_vao)
        self.plot.ctx.programs.square_line.use(self.width, z, mvp32,
                                               color=self.color,
                                               resolution=resolution)
        GL.glDrawArraysInstanced(GL.GL_TRIANGLES, 0, len(INSTANCE_GEOMETRY), 1)
