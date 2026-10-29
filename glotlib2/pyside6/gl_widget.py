import os
import traceback

from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QSurfaceFormat, QOpenGLContext
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtCore import Qt

from .. import constants


MOUSE_BUTTONS = {
    Qt.MouseButton.LeftButton    : constants.MOUSE_BUTTON_LEFT,
    Qt.MouseButton.RightButton   : constants.MOUSE_BUTTON_RIGHT,
    Qt.MouseButton.MiddleButton  : constants.MOUSE_BUTTON_MIDDLE,
    Qt.MouseButton.ExtraButton1  : None,
    Qt.MouseButton.ExtraButton2  : None,
    Qt.MouseButton.ExtraButton3  : None,
    Qt.MouseButton.ExtraButton4  : None,
    Qt.MouseButton.ExtraButton5  : None,
    Qt.MouseButton.ExtraButton6  : None,
    Qt.MouseButton.ExtraButton7  : None,
    Qt.MouseButton.ExtraButton8  : None,
    Qt.MouseButton.ExtraButton9  : None,
    Qt.MouseButton.ExtraButton10 : None,
    Qt.MouseButton.ExtraButton11 : None,
    Qt.MouseButton.ExtraButton12 : None,
    Qt.MouseButton.ExtraButton13 : None,
    Qt.MouseButton.ExtraButton14 : None,
    Qt.MouseButton.ExtraButton15 : None,
    Qt.MouseButton.ExtraButton16 : None,
    Qt.MouseButton.ExtraButton17 : None,
    Qt.MouseButton.ExtraButton18 : None,
    Qt.MouseButton.ExtraButton19 : None,
    Qt.MouseButton.ExtraButton20 : None,
    Qt.MouseButton.ExtraButton21 : None,
    Qt.MouseButton.ExtraButton22 : None,
    Qt.MouseButton.ExtraButton23 : None,
    Qt.MouseButton.ExtraButton24 : None,
}


class GLWidget(QOpenGLWidget):
    def __init__(self, window, msaa, parent=None):
        super().__init__(parent)
        self._glotlib_window = window
        self._glotlib_msaa = msaa
        self._last_ctx_size = (-1, -1)
        self._last_fb_size = (-1, -1)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        self.setMinimumSize(16, 16)
        self.setMouseTracking(True)

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
            ctx_w, ctx_h = self.width(), self.height()
            surface_dim = self.context().surface().size()
            fb_w, fb_h = surface_dim.width(), surface_dim.height()
            self._glotlib_window.ctx._init_ctx(QOpenGLContext.currentContext(),
                                               ctx_w, ctx_h, fb_w, fb_h)
        except Exception as e:
            self._dump_and_exit(e, -2)

    def resizeGL(self, w, h):
        try:
            ratio = self._glotlib_window.qt_window.devicePixelRatio()
            fb_size = (int(w * ratio), int(h * ratio))
            if fb_size != self._last_fb_size:
                self._last_fb_size = fb_size
                self._glotlib_window.ctx._tree_resize_gl_fb(*fb_size)

            ctx_size = (w, h)
            if ctx_size != self._last_ctx_size:
                self._last_ctx_size = ctx_size
                self._glotlib_window.ctx._tree_resize_gl_ctx(w, h)
        except Exception as e:
            self._dump_and_exit(e, -3)

    def paintGL(self):
        '''
        When paintGL() is called the OS has decided that we must update the
        graphics.  We HAVE to render something otherwise we end up with a blank
        screen here.
        '''
        try:
            self._glotlib_window.ctx._tree_paint_gl()
        except Exception as e:
            self._dump_and_exit(e, -4)

    def mousePressEvent(self, event):
        # Unbind any stale context for debug purposes.
        self.doneCurrent()

        mb = MOUSE_BUTTONS.get(event.button())
        if mb is None:
            return

        pos = event.position()
        y = self._glotlib_window.ctx.ctx_h - pos.y()
        self._glotlib_window.ctx._handle_mouse_button_callback(
            pos.x(), y, mb, constants.MOUSE_BUTTON_PRESS, 0)

    def mouseReleaseEvent(self, event):
        # Unbind any stale context for debug purposes.
        self.doneCurrent()

        mb = MOUSE_BUTTONS.get(event.button())
        if mb is None:
            return

        pos = event.position()
        y = self._glotlib_window.ctx.ctx_h - pos.y()
        self._glotlib_window.ctx._handle_mouse_button_callback(
            pos.x(), y, mb, constants.MOUSE_BUTTON_RELEASE, 0)

    def mouseMoveEvent(self, event):
        # Unbind any stale context for debug purposes.
        self.doneCurrent()

        pos = event.position()
        y = self._glotlib_window.ctx.ctx_h - pos.y()
        self._glotlib_window.ctx._handle_mouse_moved(pos.x(), y)
