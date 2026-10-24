import os
import traceback

from OpenGL import GL

from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QSurfaceFormat


class GLWidget(QOpenGLWidget):
    def __init__(self, window, msaa, parent=None):
        super().__init__(parent)
        self._glotlib_window = window
        self._glotlib_msaa = msaa

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
            print('initializeGL')
            self._validate_gl_profile()

            GL.glClearColor(1.0, 0.0, 0.0, 1.0)
        except Exception as e:
            self._dump_and_exit(e, -2)

    def resizeGL(self, _w, _h):
        try:
            print('resizeGL')
        except Exception as e:
            self._dump_and_exit(e, -3)

    def paintGL(self):
        try:
            print('paintGL')
            GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        except Exception as e:
            self._dump_and_exit(e, -4)
