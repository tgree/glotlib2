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


class Series:
    '''
    Hardware representation of a data series.  This encodes the vertices into
    hardware buffers using float32 representation and binds the various buffers
    to a single VAO for efficient drawing.

    Setters are provided so that the underlying vertices can be updated
    dynamically by the client.
    '''
    MIN_LEN = None

    def __init__(self, plot, vertices, color=None, width=1,
                 point_width=None, visible=True):
        self.plot        = plot
        self.vertices    = vertices
        self.color       = color
        self.width       = width
        self.point_width = point_width
        self.visible     = visible

        self.line_vao  = None
        self.vert_vbo  = None
        self.geom_vbo  = None
        self.point_vao = None

        self.plot.ctx._defer(self._init_gl)

    def _init_gl(self):
        self.line_vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.line_vao)

        self.vert_vbo = vbo.VBO(self.vertices)
        self.vert_vbo._attrib_pointer(0)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribDivisor(0, 1)

        self.vert_vbo._attrib_pointer(1, 8)
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribDivisor(1, 1)

        self.geom_vbo = vbo.StaticVBO(INSTANCE_GEOMETRY)
        self.geom_vbo._attrib_pointer(2)
        GL.glEnableVertexAttribArray(2)
        GL.glVertexAttribDivisor(2, 0)

        self.point_vao = GL.glGenVertexArrays(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vert_vbo.vbo)
        GL.glBindVertexArray(self.point_vao)
        self.vert_vbo._attrib_pointer(0)
        GL.glEnableVertexAttribArray(0)

        GL.glBindVertexArray(0)

        self._renormalize()

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def _renormalize(self):
        if len(self.vertices) == 0:
            return

        X  = self.vertices[:, 0] * self.plot.rmatrix[0][0]
        X += self.plot.rmatrix[0][3]
        Y  = self.vertices[:, 1] * self.plot.rmatrix[1][1]
        Y += self.plot.rmatrix[1][3]
        self.vert_vbo.set_x_y_data(X, Y)

    def renormalize(self):
        '''
        Recompute the normalization of the data, using the plot's
        renormalization matrix.  Called to notify us of a change to the matrix
        without any change to the original vertex data.

        This performs the normalization math in float64 format and then
        converts it down to float32 when assigning to the VBO.

        This does not directly update the GL state and is callable without an
        active OpenGL context.
        '''
        self.plot.ctx._defer(self._renormalize)

    def _set_x_data(self, X, V):
        self.vertices[:, 0] = X
        self.vert_vbo.set_x_data(V)

    def set_x_data(self, X):
        '''
        Replace the x coordinates of the original vertex data with the new X
        array and update the VBO data stored on the GPU with the normalized
        vertex data.
        '''
        X  = np.asarray(X, dtype=np.float64)
        V  = X * self.plot.rmatrix[0][0]
        V += self.plot.rmatrix[0][3]
        self.plot.ctx._defer(self._set_x_data, X, V)

    def _set_y_data(self, Y, V):
        self.vertices[:, 1] = Y
        self.vert_vbo.set_y_data(V)

    def set_y_data(self, Y):
        '''
        Replace the y coordinates of the original vertex data with the new Y
        array and update the VBO data stored on the GPU with the normalized
        vertex data.
        '''
        Y  = np.asarray(Y, dtype=np.float64)
        V  = Y * self.plot.rmatrix[1][1]
        V += self.plot.rmatrix[1][3]
        self.plot.ctx._defer(self._set_y_data, Y, V)

    def _set_x_y_data(self, vertices, X, Y):
        self.vertices = vertices
        self.vert_vbo.set_x_y_data(X, Y)

    def set_x_y_data(self, X, Y):
        X = np.asarray(X, dtype=np.float64)
        Y = np.asarray(Y, dtype=np.float64)
        vertices = np.column_stack((X, Y))

        X  = X * self.plot.rmatrix[0][0]
        X += self.plot.rmatrix[0][3]
        Y  = Y * self.plot.rmatrix[1][1]
        Y += self.plot.rmatrix[1][3]
        self.plot.ctx._defer(self._set_x_y_data, vertices, X, Y)

    def _sub_x_y_data(self, index, X, Y, V):
        overlap_v = V[:len(self.vertices) - index]
        new_v     = V[len(self.vertices) - index:]
        if len(overlap_v):
            self.vertices[-len(overlap_v):] = overlap_v
        self.vertices = np.concatenate((self.vertices, new_v))
        self.vert_vbo.sub_x_y_data(index, X, Y)

    def sub_x_y_data(self, index, X, Y):
        if len(X) == 0:
            return

        X = np.asarray(X, dtype=np.float64)
        Y = np.asarray(Y, dtype=np.float64)
        V = np.column_stack((X, Y))

        X  = X * self.plot.rmatrix[0][0]
        X += self.plot.rmatrix[0][3]
        Y  = Y * self.plot.rmatrix[1][1]
        Y += self.plot.rmatrix[1][3]
        self.plot.ctx._defer(self._sub_x_y_data, index, X, Y, V)

    def append_x_y_data(self, X, Y):
        self.sub_x_y_data(len(self.vertices), X, Y)

    def draw(self, z, mvp, resolution):
        if not self.visible:
            return

        if self.width and len(self.vert_vbo) >= 2:
            GL.glBindVertexArray(self.line_vao)
            self.plot.ctx.programs.square_line.use(self.width, z, mvp,
                                                   color=self.color,
                                                   resolution=resolution)
            GL.glDrawArraysInstanced(GL.GL_TRIANGLES, 0, len(INSTANCE_GEOMETRY),
                                     len(self.vert_vbo) - 1)

        if self.point_width and len(self.vert_vbo) >= 1:
            GL.glBindVertexArray(self.point_vao)
            self.plot.ctx.programs.frag_points.use(z, mvp, color=self.color)
            GL.glPointSize(self.point_width * self.plot.ctx.r_w)
            GL.glDrawArrays(GL.GL_POINTS, 0, len(self.vert_vbo))
