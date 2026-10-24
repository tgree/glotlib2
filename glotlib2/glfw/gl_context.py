import ctypes

import glfw

from .. import gl_context


class GLContext(gl_context.GLContext):
    def is_active(self):
        if self.opengl_context is None:
            return False

        current_context = glfw.get_current_context()
        if current_context is None:
            return False

        return (self.opengl_context ==
                ctypes.cast(current_context, ctypes.c_void_p).value)
