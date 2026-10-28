from OpenGL import GL

from .gl_object import GLObject
from .programs import Programs
from .faces import Faces
from .label import FlexLabel
from .plot import Plot
from . import matrix


# This is the padding on each side of the flexible window area.  Note that
# this amount of padding exists on the left and right sides and on the top and
# bottom sides, so the total padding is double these values.
PAD_H = 0.05
PAD_V = 0.05


def _bounds_hwp(h, w, p):
    '''
    Given a grid of height h and width w, returns the bounds (l, b, r, t) of
    the grid cell p, with coordinates as percentages of the total grid.  The
    value p is specified by numbering the grid cells as follows:

        1, 2, 3, 4,
        5, 6, 7, 8,
        ...

    Note that the first cell is numbered 1.
    '''
    p -= 1
    y  = h - (p // w) - 1
    x  = p % w

    return (x / w, y / h, (x + 1) / w, (y + 1) / h)


def _bounds_hwr(h, w, r):
    '''
    Given a grid of height h and width w, and a tuple r (p0, p1), returns the
    bounds (l, b, r, t) of the smallest rectangle fully enclosing both p0 and
    p1, with coordinates as percentages of the total grid.  The values p0 and
    p1 arespecified by numbering the grid cells as follows:

        1, 2, 3, 4,
        5, 6, 7, 8,
        ...

    Note that the first cell is numbered 1.  In the example above, the range
    (2, 7) and (7, 2) would specify the same rectangle, covering all of cells
    2, 3, 6 and 7.
    '''
    b0 = _bounds_hwp(h, w, r[0])
    b1 = _bounds_hwp(h, w, r[1])
    return (min(b0[0], b1[0]), min(b0[1], b1[1]),
            max(b0[2], b1[2]), max(b0[3], b1[3]))


def _bounds_int(b):
    '''
    Given the value b, in the range 111 to 999, interpret the value as thought
    the first digit were the height of the grid, the second digit were the
    width of the grid and the third digit was the position p in the grid, and
    then use _boudns_hwp() to compute the coordinates.
    '''
    assert 111 <= b <= 999
    h = b // 100
    w = (b % 100) // 10
    p = (b % 10)
    return _bounds_hwp(h, w, p)


def _bounds(b, pad_l=PAD_H, pad_r=PAD_H, pad_b=PAD_V, pad_t=PAD_V):
    if isinstance(b, int):
        c = _bounds_int(b)
    elif isinstance(b, tuple) and len(b) == 3 and isinstance(b[2], int):
        c = _bounds_hwp(*b)
    elif isinstance(b, tuple) and len(b) == 3 and isinstance(b[2], tuple):
        c = _bounds_hwr(*b)
    elif isinstance(b, tuple) and len(b) == 4:
        c = b
    else:
        return None

    return (pad_l + (1 - (pad_l + pad_r))*c[0],
            pad_b + (1 - (pad_b + pad_t))*c[1],
            pad_l + (1 - (pad_l + pad_r))*c[2],
            pad_b + (1 - (pad_b + pad_t))*c[3])


class GLContext(GLObject):
    def __init__(self, msaa=None):
        super().__init__(None)

        self.opengl_context = None
        self.msaa = msaa
        self.programs = Programs()
        self.faces = Faces()

        self.ctx_w = None
        self.ctx_h = None
        self.fb_w  = None
        self.fb_h  = None
        self.mvp   = None

    def is_active(self):
        '''
        Returns true if we are bound to the current thread's OpenGL context.
        '''
        raise NotImplementedError

    def _init_ctx(self, opengl_context, ctx_w, ctx_h, fb_w, fb_h):
        '''
        Called by the native window manager (or whatever is creating contexts)
        with the context bound to the current thread and handing us some
        parameters that the rest of the tree will need.
        '''
        self.opengl_context = opengl_context
        assert self.is_active()

        self.ctx_w, self.ctx_h = ctx_w, ctx_h
        self.fb_w, self.fb_h = fb_w, fb_h
        self.mvp = matrix.ortho(0, self.ctx_w, 0, self.ctx_h, -1, 1)

        self._init_gl()
        self._tree_init_new_gl_children()

    def _init_gl(self):
        '''
        Called by the native window manager (or whatever is creating contexts)
        with the context bound to the current thread.  This is where you should
        initialize OpenGL state.
        '''
        self.programs.load()

        if self.msaa is not None:
            GL.glEnable(GL.GL_MULTISAMPLE)

        GL.glClearColor(1, 1, 1, 1)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

    def _resize_gl_ctx(self, w, h):
        '''
        Called by the native window manager when the OpenGL context changes
        size.  The values are dimensions in window manager context coordinates.
        '''
        assert self.is_active()
        # print('Context Resize: %u x %u' % (w, h))
        self.ctx_w, self.ctx_h = w, h
        self.mvp = matrix.ortho(0, self.ctx_w, 0, self.ctx_h, -1, 1)

    def _resize_gl_fb(self, w, h):
        '''
        Called by the native window manager when the OpenGL framebuffer changes
        size.  The values are the dimensions in framebuffer coordinates and
        take into count things like a Retina display which has twice as many
        pixels in each dimension compares to the window manager coordinates.
        '''
        assert self.is_active()
        # print('Framebuffer Resize: %u x %u' % (w, h))
        self.fb_w, self.fb_h = w, h

    def _paint_gl(self):
        '''
        This is called when the OS has decided that the window needs to be
        redrawn, for instance due to a window resize event.  We must always
        repaint the window since everything should be considered invalidated.
        '''
        assert self.is_active()

        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    def add_label(self, *args, font=None, **kwargs):
        font = font or self.faces.vera(12)
        return FlexLabel(self, *args, font=font, **kwargs)

    def add_plot(self, bounds=111, **kwargs):
        '''
        Adds a rectangular plot to the window.  The bounds value selects the
        position of the plot and can have one of the following formats:

            HWP - a set of 3 integers encoded either as a 3-digit decimal
                  number with H, W, P in the hundreds, tens and ones positions,
                  respectively, or as a 3-tuple (H, W, P).  H and W divide the
                  window space into a grid of height H and width W and P
                  selects the grid cell numbered from 1 to H*W left-to-right
                  and then top-to-bottom.

            HWR - a 3-tuple (H, W, (r0, r1)) where the H and W values are the
                  same as HWP format but the plot rectangle will have the
                  bounds of the smallest rectangle that fully encloses both the
                  grid cells at positions r0 and r1.

            (x0, y0, x1, y1) - a 4-tuple specifying the bottom-left and top-
                  right positions of the bounding rectangle, expressed as a
                  fraction from 0 to 1 which scaled with the dimensions of the
                  enclosing window.

        The limits 4-tuple can be used to specify the (x0, y0, x1, y1) data
        limits that the plot will initially be looking at.

        The colors parameter can specify a list of (R, G, B, A) colors to cycle
        through for each new curve added to the plot, as floating-point values
        from 0 to 1.

        The max_h_ticks and max_v_ticks parameters can be used to specify the
        maximum number of ticks to display on the plot, which can be useful to
        limit spam on smaller plots.

        The aspect parameter can be either Plot.ASPECT_NONE or
        Plot.ASPECT_SQUARE, the latter which enforces the plot's data view
        edges so that squares in the data space are rendered as squares in the
        screen space.
        '''
        return Plot(self, bounds=_bounds(bounds), **kwargs)
