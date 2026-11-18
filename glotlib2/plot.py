import math

import numpy as np
from OpenGL import GL

from . import matrix
from . import constants
from . import ticker
from . import colors
from . import miter_lines
from .gl_object import GLObject
from .label import Label
from .hline import HLine
from .vline import VLine
from .vstrip import VStrip
from .series import Series
from .step_series import StepSeries


PAD_L       = 0.025
PAD_B       = 0.025
MAX_H_TICKS = 10
MAX_V_TICKS = 7


class DragState:
    def __init__(self, plot, mbs):
        self.plot            = plot
        self.mbs             = mbs
        self.click_fb_point  = plot._context_to_data(mbs.click_x, mbs.click_y)

    def handle_mouse_moved(self, x, y):
        self.plot._set_axes_from_point(self.click_fb_point, (x, y))


class NoAspect:
    @staticmethod
    def apply(wh, _ctx_wh):
        return wh

    @staticmethod
    def adjust_vert(wh, _ctx_wh):
        return wh

    @staticmethod
    def adjust_horiz(wh, _ctx_wh):
        return wh


class SquareAspect:
    @staticmethod
    def apply(wh, ctx_wh):
        '''
        Grow the dimension of the smaller axis until a square aspect ratio is
        achieved.
        '''
        ctx_aspect = ctx_wh[0] / ctx_wh[1]
        wh_aspect  = wh[0] / wh[1]
        if ctx_aspect < wh_aspect:
            return (wh[0], wh[0] / ctx_aspect)
        return (wh[1] * ctx_aspect, wh[1])

    @staticmethod
    def adjust_vert(wh, ctx_wh):
        '''
        Adjust the vertical dimension to achieve a square aspect ratio.
        '''
        ctx_aspect = ctx_wh[1] / ctx_wh[0]
        return (wh[0], wh[0] * ctx_aspect)

    @staticmethod
    def adjust_horiz(wh, ctx_wh):
        '''
        Adjust the horizontal dimension to achieve a square aspect ratio.
        '''
        ctx_aspect = ctx_wh[0] / ctx_wh[1]
        return (wh[1] * ctx_aspect, wh[1])


class Axis:
    def __init__(self):
        self.min   = -1
        self.max   = 1
        self.plots = set()

    def add(self, plot, dim):
        self.plots.add(plot)
        if dim is not None:
            self.min, self.max = dim


class Plot(GLObject):
    '''
    Class to display a plot in a GLContext.

    Data series can be added to the plot to display data points as lines, steps
    or points.  Horizontal and vertical lines can be added to annotate the data
    such as drawing origin lines or tracking the mouse position.

    As with any standard OpenGL program, we maintain a model-view-projection
    matrix.  This orthographic matrix allows us to quickly translate the camera
    and scale the data in a vertex shader so that no data buffers need to be
    updated.

    OpenGL uses 32-bit single-precision floating-point units for everything.
    In order to be able to zoom way in (which can quickly hit the precision
    limit of a float) or to pan very far from the origin (floats lose precision
    the further they get from 0) we maintain a renormalization matrix in
    addition to the MVP matrix.  When our MVP matrix gets to a point where we
    are going to start hitting the 32-bit float precision, we perform a
    renormalization step.  Renormalization takes all the original data (which
    is stored in 64-bit double-precision) and transforms a 32-bit copy so that
    the data we are trying to view gets moved to the origin and scaled so that
    the unit cube displays exactly what we were looking at before.  This
    transform is recorded in the renormalization matrix (rmatrix) and then the
    MVP matrix is reset to the unit cube.  Since the renormalization of data
    requires us to download all new vertex data to the GPU, it is an expensive
    step and only done when necessary.  The upside is that with the section of
    data that we are interested in now being situated at the origin, we have
    the full 32-bit float precision to play with again for zooming and panning.
    '''
    ASPECT_MAP = {
        constants.ASPECT_NONE   : NoAspect,
        constants.ASPECT_SQUARE : SquareAspect,
    }

    def __init__(self, gl_parent, bounds=(0, 0, 1, 1), limits=None,
                 _colors=None, max_h_ticks=MAX_H_TICKS, max_v_ticks=MAX_V_TICKS,
                 aspect=constants.ASPECT_NONE, sharex=None, sharey=None,
                 label_font=None, border_width=1, **kwargs):
        super().__init__(gl_parent, **kwargs)

        self.bounds          = bounds
        self.color_iter      = (colors.cycle(_colors)
                                if _colors else colors.cycle(colors.tab10))
        self.max_h_ticks     = max_h_ticks
        self.max_v_ticks     = max_v_ticks
        self.aspect          = Plot.ASPECT_MAP[aspect]
        self.x_axis          = sharex if sharex else Axis()
        self.y_axis          = sharey if sharey else Axis()

        # The screen coordinates of our plot.  The extend from (x, y) to
        # (x + w, y + h).  This is used all over the place for things like
        # placing objects in the right position on the window or translating
        # mouse coordinates into plot coordinates and from there into data
        # coordinates via the matrices.
        self.x = None
        self.y = None
        self.w = None
        self.h = None

        # The framebuffer coordinates of our plot.  These are inset by exactly
        # one pixel compared to the screen coordinates and then scaled by the
        # framebuffer-to-screen ratio.  These coordinates are used exclusively
        # to set the GL viewport to the plot rectangle before drawing any data
        # points.
        self.fb_x = None
        self.fb_y = None
        self.fb_w = None
        self.fb_h = None

        # Renormalization matrix and inverse.  These map a rectangle of data
        # coordinates to the range of the unit cube spanning [-1, 1] in all 3
        # dimensions.  When we zoom in too far, we approach the limits of a
        # single-precision float.  If we get too close to the limits then lines
        # displayed on the screen randomly jump around or disappear.  This can
        # also happen if we pan too far from the origin.  To correct this, we
        # do a renormalization step on the actual data points in double-
        # precision math to remap the part of the data space that we want to
        # look at to the unit cube.  This is accomplished by multiplying all
        # the original double-precision data points by the renormalization
        # matrix.  Because it requires altering all of the data buffers stored
        # on the GPU, renormalization is an expensive operation.
        self.rmatrix  = None
        self.rmatrixi = None

        # Model-view-projection matrix.  This matrix takes data points in the
        # renormalized space and maps them to screen coordinates.  Whenever a
        # renormalization event is triggered, the MVP matrix is reset to the
        # unit cube, so we render exactly the data bounded by the
        # renormalization matrix.  Then, as we zoom in or out, or pan left or
        # right, we update the MVP matrix without changing the renormalization
        # matrix, just like moving the camera around.  If we zoom in too far,
        # a renormalization event is triggered causing the actual data points
        # to be renormalized using an updated rmatrix, and then the MVP matrix
        # is reset.  The MVP matrix is stored as double-precision values, with
        # the mvp32 matrix being available as single-precision (but currently
        # unused anywhere).
        self.mvp   = None
        self.mvpi  = None
        self.mvp32 = None

        self.mouse_state     = None
        self.series          = []
        self.graph_artists   = []
        self.border_lines    = miter_lines.from_points([(0, 0)] * 6)
        self.border_width    = border_width
        self.h_ticks         = []
        self.v_ticks         = []
        self.snapped         = False
        self.label_font      = label_font or self.ctx.faces.vera(12, 0)

        if limits is not None:
            l, b, r, t = limits
            x_dim = (l, r)
            y_dim = (b, t)
        else:
            x_dim = None
            y_dim = None
        self.x_axis.add(self, x_dim)
        self.y_axis.add(self, y_dim)

        for _ in range(max_h_ticks):
            self.h_ticks.append(Label(self, (0, 0), '', font=self.label_font,
                                      anchor='N'))
        for _ in range(max_v_ticks):
            self.v_ticks.append(Label(self, (0, 0), '', font=self.label_font,
                                      anchor='E'))

        self.x_label = Label(self, (0, 0), '', font=self.label_font, anchor='N',
                             visible=False)
        self.x_label_side = 'bottom'
        self.y_label = Label(self, (0, 0), '', font=self.label_font, anchor='S',
                             visible=False, theta=math.pi / 2)
        self.y_label_side = 'left'

    def _init_gl(self):
        self._gen_bounds()

        l, r = self.x_axis.min, self.x_axis.max
        b, t = self.y_axis.min, self.y_axis.max
        l, r, b, t = self._adjust_lrbt(l, r, b, t)
        self._renormalize(l, r, b, t)
        self._gen_ticks()

    def _adjust_lrbt(self, l, r, b, t, rx=1, ry=1):
        '''
        Given l, r, b, t bounds, adjust them so that the center point of the
        rectangle is maintained but the edges grow/shrink as necessary to
        maintain the plot's data space aspect ratio.
        '''
        w    = (r - l) * rx
        h    = (t - b) * ry
        w, h = self.aspect.apply((w, h), (self.w, self.h))
        xc   = (l + r) / 2
        yc   = (b + t) / 2
        l    = xc - w / 2
        r    = xc + w / 2
        b    = yc - h / 2
        t    = yc + h / 2
        return l, r, b, t

    def _handle_resize(self):
        p_w    = self.w
        p_h    = self.h
        xc, yc = self._context_to_data(self.x + p_w / 2, self.y + p_h / 2)

        self._gen_bounds()

        if self.aspect == SquareAspect:
            n_w = self.w
            n_h = self.h
            self._set_axes_from_point((xc, yc),
                                      (self.x + n_w / 2, self.y + n_h / 2),
                                      rx=(n_w / p_w), ry=(n_h / p_h))
        else:
            self._gen_ticks()

    # If resizing breaks or becomes "elastic-y" then uncomment this.  I'd like
    # to avoid the double work though.  On glfw, we seem to get the ctx update
    # after the fb update, and the pyside6 callback has been ordered to invoke
    # the two updates with the ctx update last so it should have similar
    # behaviour.
    # def _resize_gl_fb(self, _w, _h):
    #     self._handle_resize()

    def _resize_gl_ctx(self, _w, _h):
        self._handle_resize()

    def _gen_bounds(self):
        '''
        Safe to call without an active OpenGL context, however it makes use of
        ctx and fb dimensions which are not available until after _init_gl().
        '''
        x = self.x = int((self.bounds[0] + PAD_L) * self.ctx.ctx_w)
        y = self.y = int((self.bounds[1] + PAD_B) * self.ctx.ctx_h)
        w = self.w = (int((self.bounds[2] - self.bounds[0] - PAD_L) *
                      self.ctx.ctx_w))
        h = self.h = (int((self.bounds[3] - self.bounds[1] - PAD_B) *
                      self.ctx.ctx_h))

        x += 0.5
        y += 0.5
        ps = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        vs = miter_lines.vertices_from_poly_points(ps)
        self.border_lines._update(vs)

        x += 0.5
        y += 0.5
        w -= 1
        h -= 1
        self.fb_x  = round(x * self.ctx.fb_w / self.ctx.ctx_w)
        self.fb_y  = round(y * self.ctx.fb_h / self.ctx.ctx_h)
        self.fb_w  = round(w * self.ctx.fb_w / self.ctx.ctx_w)
        self.fb_h  = round(h * self.ctx.fb_h / self.ctx.ctx_h)

    def _renormalize(self, l, r, b, t):
        '''
        Renormalizes the data but does not update any GL state.  Callable
        without an active OpenGL context.  This is the only place that the
        renormalization matrix is changed and is expensive because it
        requires all graph artists to renormalize their data sets.
        '''
        # Note: If this update is because we are near the float precision
        # limit, then this is just the equivalent of setting rmatrix to
        # mvp @ rmatrix and then setting mvp to the unit cube.  We also call
        # this when first initializing the matrices, in which case they will
        # both be None and we can't just do that matrix multiply on them.
        # Renormalization may also take place if we randomly jump to a new
        # data location (say by snapping to the data with the space bar) and
        # the float precision at the new location is no longer acceptable.
        self.rmatrix  = matrix.ortho(l, r, b, t, -1, 1, dtype=np.float64)
        self.rmatrixi = matrix.unortho(l, r, b, t, -1, 1, dtype=np.float64)
        self.mvp      = matrix.ortho(-1, 1, -1, 1, -1, 1, dtype=np.float64)
        self.mvpi     = matrix.unortho(-1, 1, -1, 1, -1, 1, dtype=np.float64)
        self.mvp32    = np.array(self.mvp, dtype=np.float32)
        for ga in self.graph_artists:
            ga.renormalize()

    def _gen_ticks(self):
        l, r = self.x_axis.min, self.x_axis.max
        b, t = self.y_axis.min, self.y_axis.max

        ticks, texts = ticker.gen_ticks_and_texts(l, r, Nmax=self.max_h_ticks)
        for i, h_t in enumerate(self.h_ticks):
            if i < len(ticks):
                x = (ticks[i] - l) * self.w / (r - l)
                h_t.set_pos((self.x + x, self.y))
                h_t.set_text(texts[i])
            else:
                h_t.pos = (0, 0)
                h_t.set_text('')

        ticks, texts = ticker.gen_ticks_and_texts(b, t, Nmax=self.max_v_ticks)
        for i, v_t in enumerate(self.v_ticks):
            if i < len(ticks):
                y = int((ticks[i] - b) * self.h / (t - b))
                v_t.set_pos((self.x - 2, self.y + y + 2))
                v_t.set_text(texts[i])
            else:
                v_t.pos = (0, 0)
                v_t.set_text('')

        self._gen_labels()

    def _gen_labels(self):
        if self.x_label_side == 'bottom':
            # The height of the X-axis tick numbers are always the height of
            # the tick (label) font.
            # x_ticks_height = self.label_font.ascender
            x_ticks_height = max(h_t.height for h_t in self.h_ticks)
            self.x_label.set_pos((self.x + self.w / 2,
                                  self.y - x_ticks_height - 6))
        else:
            self.x_label.set_pos((self.x + self.w / 2, self.y + self.h + 18))

        if self.y_label_side == 'left':
            # The width of the Y-axis tick numbers depends on the number of
            # digits and sign being displayed, so we need to calculate it
            # directly.
            y_ticks_width = max(v_t.width for v_t in self.v_ticks)
            self.y_label.set_pos((self.x - y_ticks_width -
                                  (self.label_font.size + 4),
                                  self.y + self.h / 2))
        else:
            self.y_label.set_pos((self.x + self.w + self.label_font.size + 4,
                                  self.y + self.h / 2))

    def _gen_mvp_from_axes(self):
        '''
        Generates mvp and mvpi such that we will be viewing the specified
        rectangle of data dimensions.  This is a simple orthographic
        projection.
        '''
        l, r = self.x_axis.min, self.x_axis.max
        b, t = self.y_axis.min, self.y_axis.max
        ml, mb, _, _ = self.rmatrix @ (l, b, 0, 1)
        mr, mt, _, _ = self.rmatrix @ (r, t, 0, 1)
        self.mvp   = matrix.ortho(ml, mr, mb, mt, -1, 1, dtype=np.float64)
        self.mvpi  = matrix.unortho(ml, mr, mb, mt, -1, 1, dtype=np.float64)
        self.mvp32 = np.array(self.mvp, dtype=np.float32)

        K        = 2**(23 - 2)
        ctx_w    = self.w
        ctx_h    = self.h
        mvp_w    = 2 * self.mvpi[0][0]
        mvp_h    = 2 * self.mvpi[1][1]
        max_x    = max(abs(ml), abs(mr))
        max_y    = max(abs(mb), abs(mt))
        renorm_x = (max_x > mvp_w * K / ctx_w)
        renorm_y = (max_y > mvp_h * K / ctx_h)
        if renorm_x or renorm_y:
            self._renormalize(l, r, b, t)

        self._gen_ticks()
        self.snapped = False

        self.ctx.mark_dirty()

    def _set_axes_from_limits(self, l, r, b, t):
        '''
        Updates the axes so that we will be viewing the specified rectangle of
        data dimensions, then triggers all plots to update as necessary.
        '''
        self.x_axis.min, self.x_axis.max = l, r
        self.y_axis.min, self.y_axis.max = b, t
        plots = (self.x_axis.plots | self.y_axis.plots)
        for p in plots:
            p._gen_mvp_from_axes()

    def _set_axes_from_dimensions_and_point(self, w, h, d_point, p_point):
        '''
        Updates the axes such that we will be viewing a rectangle of data
        dimensions w x h with the (x, y) data point d_point locked to the
        center of the (x, y) plot pixel p_point.
        '''
        p_x_ratio  = (p_point[0] - self.x) / self.w
        p_y_ratio  = (p_point[1] - self.y) / self.h
        l          = d_point[0] - p_x_ratio * w
        r          = l + w
        b          = d_point[1] - p_y_ratio * h
        t          = b + h
        self._set_axes_from_limits(l, r, b, t)

    def _set_axes_from_point(self, d_point, p_point, rx=1, ry=1):
        '''
        Updates the axes such that the current dimensions are unchanged (or
        optionally multiplied by rx and ry) but data point d_point will appear
        under the plot pixel p_point.
        '''
        w = rx * 2 * self.mvpi[0][0] * self.rmatrixi[0][0]
        h = ry * 2 * self.mvpi[1][1] * self.rmatrixi[1][1]
        self._set_axes_from_dimensions_and_point(w, h, d_point, p_point)

    def _context_to_data(self, x, y):
        '''
        Converts a GLContext coordinate to a data coordinate.
        '''
        x = 2 * (x - self.x) / self.w - 1
        y = 2 * (y - self.y) / self.h - 1
        v = self.rmatrixi @ self.mvpi @ (x, y, 0, 1)
        return v[0], v[1]

    def _data_to_context(self, x, y):
        '''
        Converts a data coordinate to a GLContext coordinate.
        '''
        x, y, _, _ = self.mvp @ self.rmatrix @ (x, y, 0, 1)
        y = (y + 1) * self.h / 2 + self.y
        x = (x + 1) * self.w / 2 + self.x
        return x, y

    def _datas_to_contexts(self, X, Y):
        '''
        Converts arrays of data coordinates to arrays of GLContext coordinates.
        '''
        zeros       = np.zeros_like(X)
        ones        = np.ones_like(X)
        points      = np.vstack([X, Y, zeros, ones])
        transformed = self.mvp @ self.rmatrix @ points
        tx, ty      = transformed[0], transformed[1]
        out_y = (ty + 1) * self.h / 2 + self.y
        out_x = (tx + 1) * self.w / 2 + self.x
        return out_x, out_y

    def handle_mouse_down(self, mbs):
        if self.mouse_state:
            return
        if mbs.mods:
            return
        if mbs.button != constants.MOUSE_BUTTON_LEFT:
            return

        self.mouse_state = DragState(self, mbs)

    def handle_mouse_moved(self, x, y):
        if self.mouse_state:
            self.mouse_state.handle_mouse_moved(x, y)

    def handle_mouse_up(self, mbs):
        if not self.mouse_state:
            return
        if mbs.button != self.mouse_state.mbs.button:
            return

        self.mouse_state = None

    def handle_mouse_scrolled(self, x, y, dx, dy, mods):
        dx = max(dx, -99)
        dx = min(dx, 99)
        dy = max(dy, -99)
        dy = min(dy, 99)
        if self.aspect == SquareAspect:
            rx = ry = 1 - dy / 100
        elif (mods & constants.MOD_ANY_SHIFT):
            rx = 1 + dx / 100
            ry = 1 - dy / 100
        elif (mods & constants.MOD_ANY_ALT):
            rx = 1
            ry = 1 - dy / 100
        else:
            rx = ry = 1 - dy / 100

        fx, fy = self._context_to_data(x, y)
        self._set_axes_from_point((fx, fy), (x, y), rx=rx, ry=ry)

    def _add_series(self, cls, points=None, X=None, Y=None, color=None,
                    **kwargs):
        color = colors.make(color, self.color_iter)

        if points is not None:
            vs = np.array(points, dtype=np.float64)
        elif X is not None and Y is not None:
            vs = np.column_stack((X, Y)).astype(np.float64, copy=False)
        else:
            vs = np.column_stack(([], [])).astype(np.float64, copy=False)

        s = cls(self, vs, color=color, **kwargs)
        self.series.append(s)
        self.graph_artists.append(s)
        return s

    def add_lines(self, points=None, **kwargs):
        '''
        Adds a set of Lines joining all the specified points.  The points can
        be encoded in a list of (x, y) tuples using the points keyword argument,
        or they can be encoded as separate lists of X and Y coordinates using
        the X and Y keyword arguments.
        '''
        return self._add_series(Series, points=points, **kwargs)

    def add_points(self, points=None, width=1, **kwargs):
        '''
        Adds a set of Points at the specified points.  The points can be
        encoded in a list of (x, y) tuples using the points keyword argument,
        or they can be encoded as separate lists of X and Y coordinates using
        the X and Y keyword arguments.
        '''
        return self._add_series(Series, points=points, width=None,
                                point_width=width, **kwargs)

    def add_steps(self, points=None, **kwargs):
        '''
        Adds a set of steps between the specified points.
        '''
        return self._add_series(StepSeries, points=points, **kwargs)

    def add_hline(self, y, color=None, **kwargs):
        '''
        Adds a horizontal line at the specified y coordinate.
        '''
        color = colors.make(color, self.color_iter)
        hl    = HLine(self, y, color=color, **kwargs)
        self.graph_artists.append(hl)
        return hl

    def add_vline(self, x, color=None, **kwargs):
        '''
        Adds a vertical line at the specified x coordinate.
        '''
        color = colors.make(color, self.color_iter)
        vl    = VLine(self, x, color=color, **kwargs)
        self.graph_artists.append(vl)
        return vl

    def add_vstrip(self, x1, x2, color=None, **kwargs):
        '''
        Adds a vertical strip between the specified x coordinates.
        '''
        color = colors.make(color, self.color_iter)
        vs    = VStrip(self, x1, x2, color=color, **kwargs)
        self.graph_artists.append(vs)
        return vs

    def _snap_bounds(self):
        l = b = math.inf
        r = t = -math.inf
        for s in self.series:
            if not s.visible or len(s.vertices) == 0:
                continue

            cleaned = np.where(np.isfinite(s.vertices), s.vertices, np.nan)
            sl, sb = np.nanmin(cleaned, axis=0)
            sr, st = np.nanmax(cleaned, axis=0)
            l = min(l, sl)
            b = min(b, sb)
            r = max(r, sr)
            t = max(t, st)
        if l == r:
            l -= 0.5
            r += 0.5
        if b == t:
            b -= 0.5
            t += 0.5
        if l < r and b < t:
            l, r, b, t = self._adjust_lrbt(l, r, b, t, 1.05, 1.05)
            self._set_axes_from_limits(l, r, b, t)

        self.snapped = True

    def snap_bounds(self):
        self.ctx._defer(self._snap_bounds)

    def _set_x_lim(self, l, r):
        b, t = self.y_axis.min, self.y_axis.max
        _, h = self.aspect.adjust_vert((r - l, t - b), (self.w, self.h))
        b    = (b + t - h) / 2
        t    = (b + t + h) / 2
        self._set_axes_from_limits(l, r, b, t)

    def set_x_lim(self, l, r):
        self.ctx._defer(self._set_x_lim, l, r)

    def _set_y_lim(self, b, t):
        l, r = self.x_axis.min, self.x_axis.max
        w, _ = self.aspect.adjust_horiz((r - l, t - b), (self.w, self.h))
        l    = (l + r - w) / 2
        r    = (l + r + w) / 2
        self._set_axes_from_limits(l, r, b, t)

    def set_y_lim(self, b, t):
        self.ctx._defer(self._set_y_lim, b, t)

    def _set_x_label(self, t, side='bottom'):
        self.x_label.set_text(t)
        if t != '':
            self.x_label.show()
        else:
            self.x_label.hide()
        self.x_label_side = side
        self._gen_labels()

    def set_x_label(self, t, side='bottom'):
        self.ctx._defer(self._set_x_label, t, side=side)

    def _set_y_label(self, t, side='left'):
        self.y_label.set_text(t)
        if t != '':
            self.y_label.show()
        else:
            self.y_label.hide()
        self.y_label_side = side
        self._gen_labels()

    def set_y_label(self, t, side='left'):
        self.ctx._defer(self._set_y_label, t, side=side)

    def set_bounds(self, bounds, **kwargs):
        self.ctx._defer(self.ctx.set_plot_bounds, self, bounds, **kwargs)

    def _paint_gl(self):
        GL.glViewport(0, 0, self.ctx.fb_w, self.ctx.fb_h)

        self.border_lines.bind(0)
        self.border_lines.use_program(self.ctx, self.border_width, 0,
                                      self.ctx.mvp, (0, 0, 0, 1),
                                      (self.ctx.ctx_w, self.ctx.ctx_h))
        self.border_lines.draw()

        GL.glViewport(self.fb_x, self.fb_y, self.fb_w, self.fb_h)
        for ga in self.graph_artists:
            ga.draw(0, self.mvp32, (self.w, self.h))

        GL.glViewport(0, 0, self.ctx.fb_w, self.ctx.fb_h)
