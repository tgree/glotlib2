from PySide6.QtGui import QOpenGLContext

from .. import gl_context


class GLContext(gl_context.GLContext):
    def is_active(self):
        if self.opengl_context is None:
            return False
        return self.opengl_context == QOpenGLContext.currentContext()
