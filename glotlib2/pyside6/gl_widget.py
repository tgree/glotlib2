import os
import traceback

from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QSurfaceFormat, QOpenGLContext


class GLWidget(QOpenGLWidget):
    def __init__(self, window, msaa, parent=None):
        super().__init__(parent)
        self._glotlib_window = window
        self._glotlib_msaa = msaa
        self._last_ctx_size = (-1, -1)
        self._last_fb_size = (-1, -1)

    def _validate_gl_profile(self):
        if (self.context().format().profile() !=
                QSurfaceFormat.OpenGLContextProfile.CoreProfile):
            print('GLOTLIB ERROR: Failed to secure Core Profile. '
                  'Did you call glotlib.pyside6.init_backend()?')
            os._exit(-1)

    def _dump_and_exit(self, _e, rv):
        print(traceback.format_exc())
        os._exit(rv)

    def initializeGL(self):
        try:
            self._validate_gl_profile()
            self._glotlib_window.ctx._init_gl(QOpenGLContext.currentContext())
        except Exception as e:
            self._dump_and_exit(e, -2)

    def resizeGL(self, w, h):
        try:
            ctx_size = (w, h)
            if ctx_size != self._last_ctx_size:
                self._last_ctx_size = ctx_size
                self._glotlib_window.ctx._resize_gl_ctx(w, h)

            ratio = self._glotlib_window.qt_window.devicePixelRatio()
            fb_size = (int(w * ratio), int(h * ratio))
            if fb_size != self._last_fb_size:
                self._last_fb_size = fb_size
                self._glotlib_window.ctx._resize_gl_fb(*fb_size)
        except Exception as e:
            self._dump_and_exit(e, -3)

    def paintGL(self):
        '''
        When paintGL() is called the OS has decided that we must update the
        graphics.  We HAVE to render something otherwise we end up with a blank
        screen here.
        '''
        try:
            self._glotlib_window.ctx._paint_gl()
        except Exception as e:
            self._dump_and_exit(e, -4)
