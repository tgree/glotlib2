import math
from ctypes import c_void_p

import numpy as np
from OpenGL import GL


def ceil_pow2(v):
    return (1 << math.ceil(math.log2(v)))


class VBO:
    '''
    This class holds a set of (x, y) vertices in float32 format, bound to a
    hardware VBO.
    '''
    def __init__(self, ctx, vertices, gl_type=GL.GL_DYNAMIC_DRAW):
        # Model fields.
        self.ctx           = ctx
        self.init_vertices = np.array(vertices, dtype=np.float32)
        self.vertices      = self.init_vertices
        self.gl_type       = gl_type
        self.ncomponents   = 2    # Always (x, y) for now.
        self.capacity      = 0

        # Data fields.
        self.vbo = None

    def __len__(self):
        return len(self.vertices)

    def set_x_data(self, X):
        '''
        Replaces the first component of all vertices with the specified X
        values, which must have as many elements as the length of the current
        vertices list.  Alternatively, X may be a scalar instead of an array
        and that value will be assigned to all vertices.
        '''
        self.vertices[:, 0] = X
        self.ctx._defer(self._sub_vbo_range, 0, len(self.vertices),
                        self.vertices)

    def set_y_data(self, Y):
        '''
        Replaces the seconds component of all vertices with the specified Y
        values, which must have as many elements as the length of the current
        vertices list.  Alternatively, Y may be a scalar instead of an array
        and that value will be assigned to all vertices.
        '''
        self.vertices[:, 1] = Y
        self.ctx._defer(self._sub_vbo_range, 0, len(self.vertices),
                        self.vertices)

    def set_x_y_data(self, X, Y):
        '''
        Replaces the VBO with completely new X and Y data, which may have
        different length than the existing data.  The backing buffer remains at
        its current capacity.
        '''
        self.vertices = np.column_stack((
            np.asarray(X, dtype=np.float32),
            np.asarray(Y, dtype=np.float32)
        ))
        self.ctx._defer(self._sub_vbo_range, 0, len(X), self.vertices)

    def sub_x_y_data(self, index, X, Y):
        '''
        Substitutes X and Y components starting at the specified index.  The
        data will be extended if the data to be substituted in goes past the
        end of the existing data.
        '''
        assert len(X) == len(Y)
        assert index <= len(self.vertices)
        sub_data = np.column_stack((
            np.asarray(X, dtype=np.float32),
            np.asarray(Y, dtype=np.float32)
        ))
        self.vertices = np.concatenate((
            self.vertices[:index],
            sub_data,
            self.vertices[index + len(X):]
        ))
        self.ctx._defer(self._sub_vbo_range, index, len(X), self.vertices)

    def _init_gl(self):
        '''
        Allocate the GL buffer and set its initial data.  Leaves the buffer
        bound to GL_ARRAY_BUFFER.
        '''
        self.vbo = GL.glGenBuffers(1)
        self._sub_vbo_range(0, len(self.init_vertices), self.init_vertices)
        self.init_vertices = None

    def _sub_vbo_range(self, index, N, vertices):
        '''
        Writes vertices to the VBO starting at index, enlarging the VBO buffer
        if necessary.
        '''
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)

        # Enlarge the VBO and copy it all in if necessary.
        if self.capacity < index + N:
            self.capacity = ceil_pow2(index + N)
            GL.glBufferData(GL.GL_ARRAY_BUFFER,
                            4 * self.ncomponents * self.capacity,
                            None, self.gl_type)
            index = 0
            N = len(vertices)

        # Sub in the new data.
        offset = 4 * self.ncomponents * index
        size   = 4 * self.ncomponents * N
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, offset, size,
                           vertices[index:index + N])

    def _attrib_pointer(self, unit, offset=0):
        GL.glVertexAttribPointer(unit, self.ncomponents, GL.GL_FLOAT,
                                 GL.GL_FALSE, 0, c_void_p(offset))


class StaticVBO(VBO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, gl_type=GL.GL_STATIC_DRAW, **kwargs)


class DynamicVBO(VBO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, gl_type=GL.GL_DYNAMIC_DRAW, **kwargs)
