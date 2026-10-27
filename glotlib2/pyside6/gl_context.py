from PySide6.QtGui import QOpenGLContext
from PySide6.QtCore import QMetaObject, Qt

from .. import gl_context


class GLContext(gl_context.GLContext):
    def __init__(self, gl_widget, **kwargs):
        super().__init__(**kwargs)

        self._gl_widget = gl_widget

    def is_active(self):
        if self.opengl_context is None:
            return False
        return self.opengl_context == QOpenGLContext.currentContext()

    def mark_dirty(self):
        QMetaObject.invokeMethod(self._gl_widget, 'update',
                                 Qt.ConnectionType.QueuedConnection)
