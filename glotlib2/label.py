from ctypes import c_void_p
from enum import IntEnum

from OpenGL import GL

from .gl_object import GLObject
from . import matrix


class HAlign(IntEnum):
    LEFT    = 0
    MIDDLE  = 1
    RIGHT   = 2


class VAlign(IntEnum):
    BOTTOM  = 0
    MIDDLE  = 1
    TOP     = 2


ALIGNMENTS = {
    'N'     : (HAlign.MIDDLE,   VAlign.TOP),
    'NE'    : (HAlign.RIGHT,    VAlign.TOP),
    'E'     : (HAlign.RIGHT,    VAlign.MIDDLE),
    'SE'    : (HAlign.RIGHT,    VAlign.BOTTOM),
    'S'     : (HAlign.MIDDLE,   VAlign.BOTTOM),
    'SW'    : (HAlign.LEFT,     VAlign.BOTTOM),
    'W'     : (HAlign.LEFT,     VAlign.MIDDLE),
    'NW'    : (HAlign.LEFT,     VAlign.TOP),
    'C'     : (HAlign.MIDDLE,   VAlign.MIDDLE),
}


class Label(GLObject):
    def __init__(self, ctx, gl_parent, pos, text, face=None, font_size=None,
                 font_oversample_log2=0, theta=0, anchor='SW',
                 color=(0, 0, 0, 1), visible=True):
        assert face
        assert font_size

        super().__init__(gl_parent)

        self.ctx                  = ctx
        self.font                 = None
        self.face                 = face
        self.font_size            = font_size
        self.font_oversample_log2 = font_oversample_log2
        self.pos                  = (int(pos[0]), int(pos[1]))
        self.theta                = theta
        self.color                = color
        self.visible              = visible
        self.text                 = None
        self.new_text             = text
        self.mvp                  = None
        alignment                 = ALIGNMENTS[anchor]
        self.halign               = alignment[0]
        self.valign               = alignment[1]
        self.width                = 0
        self.height               = 0
        self.nvertices            = 0
        self.vao                  = None
        self.geom_vbo             = None
        self.tex_vbo              = None

    def _init_gl(self):
        self.font     = self.face(self.font_size,
                                  oversample_log2=self.font_oversample_log2)
        self.vao      = GL.glGenVertexArrays(1)
        self.geom_vbo = GL.glGenBuffers(1)
        self.tex_vbo  = GL.glGenBuffers(1)

        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.geom_vbo)
        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 0, c_void_p(0))
        GL.glEnableVertexAttribArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.tex_vbo)
        GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 0, c_void_p(0))
        GL.glEnableVertexAttribArray(1)

        self._gen_text_vertices(self.new_text)

    def _paint_gl(self):
        if self.new_text != self.text:
            self._gen_text_vertices(self.new_text)
        if not self.nvertices:
            return

        mvp = self.ctx.mvp @ self.mvp
        GL.glBindVertexArray(self.vao)
        self.font.bind(0)
        self.ctx.programs.text.use(0, mvp, self.font, color=self.color)
        GL.glEnable(GL.GL_BLEND)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.nvertices)
        GL.glDisable(GL.GL_BLEND)

    def _update_mvp(self):
        dx = round(self.width * self.halign / 2)
        dy = round(self.height * self.valign / 2)
        self.mvp = (
            matrix.translate(*self.pos) @
            matrix.rotate(self.theta) @
            matrix.translate(-dx, -dy)
            )

    def _gen_text_vertices(self, text):
        if text == self.text:
            return False

        vertices, tex_coords, width, height = self.font.gen_vertices_left(text)

        self.text      = text
        self.nvertices = len(vertices)
        self.width     = width
        self.height    = height
        if self.nvertices:
            GL.glBindVertexArray(self.vao)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.geom_vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices, GL.GL_STATIC_DRAW)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.tex_vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER, tex_coords, GL.GL_STATIC_DRAW)

        self._update_mvp()
        return True

    def _set_text(self, text):
        self.new_text = text

    def _set_pos(self, pos):
        self.pos = (int(pos[0]), int(pos[1]))
        self._update_mvp()

    def _set_theta(self, theta):
        self.theta = theta
        self._update_mvp()

    def draw_batched(self):
        if self.new_text != self.text:
            self._gen_text_vertices(self.new_text)
        if not self.nvertices or not self.visible:
            return

        mvp = self.ctx.mvp @ self.mvp
        self.ctx.programs.text.uniformMatrix4fv('u_mvp', mvp)
        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, self.nvertices)

    def set_text(self, text):
        self._set_text(text)
        self.ctx.mark_dirty()

    def set_pos(self, pos):
        self._set_pos(pos)
        self.ctx.mark_dirty()

    def set_theta(self, theta):
        self._set_theta(theta)
        self.ctx.mark_dirty()

    def show(self):
        self.visible = True
        self.ctx.mark_dirty()

    def hide(self):
        self.visible = False
        self.ctx.mark_dirty()


class FlexLabel(Label):
    def __init__(self, ctx, gl_parent, pos, *args, **kwargs):
        super().__init__(ctx, gl_parent, (0, 0), *args, **kwargs)
        self.flex_pos = pos

    def _init_gl(self):
        self.pos = (int(self.flex_pos[0] * self.ctx.ctx_w),
                    int(self.flex_pos[1] * self.ctx.ctx_h))
        super()._init_gl()

    def _resize_gl_ctx(self, w, h):
        self._set_flex_pos(self.flex_pos)

    def _set_flex_pos(self, pos):
        self.flex_pos = pos
        pos           = (pos[0] * self.ctx.ctx_w,
                         pos[1] * self.ctx.ctx_h)
        super()._set_pos(pos)

    def set_pos(self, pos):
        self._set_flex_pos(pos)
        self.ctx.mark_dirty()
