import ctypes

import glfw

from .. import gl_context


class GLContext(gl_context.GLContext):
    def __init__(self, glfw_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dirty = False
        self._glfw_window = glfw_window

    def is_active(self):
        if self.opengl_context is None:
            return False

        current_context = glfw.get_current_context()
        if current_context is None:
            return False

        return (self.opengl_context ==
                ctypes.cast(current_context, ctypes.c_void_p).value)

    def _get_cursor_pos(self):
        x, y = glfw.get_cursor_pos(self._glfw_window)
        return x, self.ctx_h - y

    def mark_dirty(self):
        self._dirty = True
        glfw.post_empty_event()
