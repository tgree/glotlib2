import os
import traceback

from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QSurfaceFormat, QOpenGLContext
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtCore import Qt

from .. import constants
from .gl_context import GLContext


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


PYSIDE_KEYMAP_TO_GLOTLIB = {
    Qt.Key.Key_A            : 'a',
    Qt.Key.Key_B            : 'b',
    Qt.Key.Key_C            : 'c',
    Qt.Key.Key_D            : 'd',
    Qt.Key.Key_E            : 'e',
    Qt.Key.Key_F            : 'f',
    Qt.Key.Key_G            : 'g',
    Qt.Key.Key_H            : 'h',
    Qt.Key.Key_I            : 'i',
    Qt.Key.Key_J            : 'j',
    Qt.Key.Key_K            : 'k',
    Qt.Key.Key_L            : 'l',
    Qt.Key.Key_M            : 'm',
    Qt.Key.Key_N            : 'n',
    Qt.Key.Key_O            : 'o',
    Qt.Key.Key_P            : 'p',
    Qt.Key.Key_Q            : 'q',
    Qt.Key.Key_R            : 'r',
    Qt.Key.Key_S            : 's',
    Qt.Key.Key_T            : 't',
    Qt.Key.Key_U            : 'u',
    Qt.Key.Key_V            : 'v',
    Qt.Key.Key_W            : 'w',
    Qt.Key.Key_X            : 'x',
    Qt.Key.Key_Y            : 'y',
    Qt.Key.Key_Z            : 'z',
    Qt.Key.Key_0            : '0',
    Qt.Key.Key_1            : '1',
    Qt.Key.Key_2            : '2',
    Qt.Key.Key_3            : '3',
    Qt.Key.Key_4            : '4',
    Qt.Key.Key_5            : '5',
    Qt.Key.Key_6            : '6',
    Qt.Key.Key_7            : '7',
    Qt.Key.Key_8            : '8',
    Qt.Key.Key_9            : '9',
    Qt.Key.Key_Space        : ' ',
    Qt.Key.Key_Return       : '\r',
    Qt.Key.Key_Escape       : constants.KEY_ESCAPE,
    Qt.Key.Key_Backspace    : '\b',
    Qt.Key.Key_Delete       : constants.KEY_DELETE,
    Qt.Key.Key_Tab          : '\t',
    Qt.Key.Key_Up           : constants.KEY_UP_ARROW,
    Qt.Key.Key_Down         : constants.KEY_DOWN_ARROW,
    Qt.Key.Key_Left         : constants.KEY_LEFT_ARROW,
    Qt.Key.Key_Right        : constants.KEY_RIGHT_ARROW,
    Qt.Key.Key_PageUp       : constants.KEY_PAGE_UP,
    Qt.Key.Key_PageDown     : constants.KEY_PAGE_DOWN,
    Qt.Key.Key_Home         : constants.KEY_HOME,
    Qt.Key.Key_End          : constants.KEY_END,
    Qt.Key.Key_Shift        : constants.KEY_LEFT_SHIFT,     # !!!
    Qt.Key.Key_Control      : constants.KEY_LEFT_CONTROL,   # !!!
    Qt.Key.Key_Alt          : constants.KEY_LEFT_ALT,       # !!!
    Qt.Key.Key_Meta         : constants.KEY_LEFT_SUPER,     # !!!, macOS Command
    Qt.Key.Key_QuoteLeft    : '`',
    Qt.Key.Key_Apostrophe   : "'",
    Qt.Key.Key_Minus        : '-',
    Qt.Key.Key_Equal        : '=',
    Qt.Key.Key_BracketLeft  : '[',
    Qt.Key.Key_BracketRight : ']',
    Qt.Key.Key_Semicolon    : ';',
    Qt.Key.Key_Backslash    : '\\',
    Qt.Key.Key_Comma        : ',',
    Qt.Key.Key_Period       : '.',
    Qt.Key.Key_Slash        : '/',
    Qt.Key.Key_Enter        : constants.KEYPAD_ENTER,
    Qt.Key.Key_CapsLock     : constants.KEY_CAPS_LOCK,
    Qt.Key.Key_F1           : constants.KEY_F1,
    Qt.Key.Key_F2           : constants.KEY_F2,
    Qt.Key.Key_F3           : constants.KEY_F3,
    Qt.Key.Key_F4           : constants.KEY_F4,
    Qt.Key.Key_F5           : constants.KEY_F5,
    Qt.Key.Key_F6           : constants.KEY_F6,
    Qt.Key.Key_F7           : constants.KEY_F7,
    Qt.Key.Key_F8           : constants.KEY_F8,
    Qt.Key.Key_F9           : constants.KEY_F9,
    Qt.Key.Key_F10          : constants.KEY_F10,
    Qt.Key.Key_F11          : constants.KEY_F11,
    Qt.Key.Key_F12          : constants.KEY_F12,
    Qt.Key.Key_F13          : constants.KEY_F13,
    Qt.Key.Key_F14          : constants.KEY_F14,
    Qt.Key.Key_F15          : constants.KEY_F15,
    Qt.Key.Key_F16          : constants.KEY_F16,
    Qt.Key.Key_F17          : constants.KEY_F17,
    Qt.Key.Key_F18          : constants.KEY_F18,
    Qt.Key.Key_F19          : constants.KEY_F19,
    Qt.Key.Key_F20          : constants.KEY_F20,
    Qt.Key.Key_F21          : constants.KEY_F21,
    Qt.Key.Key_F22          : constants.KEY_F22,
    Qt.Key.Key_F23          : constants.KEY_F23,
    Qt.Key.Key_F24          : constants.KEY_F24,
    Qt.Key.Key_F25          : constants.KEY_F25,
    Qt.Key.Key_Insert       : constants.KEY_INSERT,
    Qt.Key.Key_Menu         : constants.KEY_MENU,
    Qt.Key.Key_NumLock      : constants.KEY_NUM_LOCK,
    Qt.Key.Key_Pause        : constants.KEY_PAUSE,
    Qt.Key.Key_Print        : constants.KEY_PRINT_SCREEN,
    Qt.Key.Key_ScrollLock   : constants.KEY_SCROLL_LOCK,
    Qt.Key.Key_unknown      : None,
}

# These keys are active if event.modifiers() has the bitmask
# Qt.KeyboardModifier.KeypadModifier set.
PYSIDE_KEYPAD_KEYS = {
    Qt.Key.Key_0            : constants.KEYPAD_0,
    Qt.Key.Key_1            : constants.KEYPAD_1,
    Qt.Key.Key_2            : constants.KEYPAD_2,
    Qt.Key.Key_3            : constants.KEYPAD_3,
    Qt.Key.Key_4            : constants.KEYPAD_4,
    Qt.Key.Key_5            : constants.KEYPAD_5,
    Qt.Key.Key_6            : constants.KEYPAD_6,
    Qt.Key.Key_7            : constants.KEYPAD_7,
    Qt.Key.Key_8            : constants.KEYPAD_8,
    Qt.Key.Key_9            : constants.KEYPAD_9,
    Qt.Key.Key_Period       : constants.KEYPAD_DOT,
    Qt.Key.Key_Slash        : constants.KEYPAD_DIVIDE,
    Qt.Key.Key_Asterisk     : constants.KEYPAD_MULTIPLY,
    Qt.Key.Key_Minus        : constants.KEYPAD_MINUS,
    Qt.Key.Key_Plus         : constants.KEYPAD_PLUS,
    Qt.Key.Key_Equal        : constants.KEYPAD_EQUALS,
}


class GLWidget(QOpenGLWidget):
    def __init__(self, msaa, parent=None, delegate=None):
        super().__init__(parent)
        self._last_ctx_size = (-1, -1)
        self._last_fb_size = (-1, -1)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)
        self.setMinimumSize(16, 16)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.ctx = GLContext(self, msaa=msaa, delegate=delegate)

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
            self.ctx._init_ctx(QOpenGLContext.currentContext(), ctx_w, ctx_h,
                               fb_w, fb_h)
        except Exception as e:
            self._dump_and_exit(e, -2)

    def resizeGL(self, w, h):
        try:
            ratio = self.devicePixelRatio()
            fb_size = (int(w * ratio), int(h * ratio))
            if fb_size != self._last_fb_size:
                self._last_fb_size = fb_size
                self.ctx._tree_resize_gl_fb(*fb_size)

            ctx_size = (w, h)
            if ctx_size != self._last_ctx_size:
                self._last_ctx_size = ctx_size
                self.ctx._tree_resize_gl_ctx(w, h)
        except Exception as e:
            self._dump_and_exit(e, -3)

    def paintGL(self):
        '''
        When paintGL() is called the OS has decided that we must update the
        graphics.  We HAVE to render something otherwise we end up with a blank
        screen here.
        '''
        try:
            self.ctx._tree_paint_gl()
        except Exception as e:
            self._dump_and_exit(e, -4)

    def mousePressEvent(self, event):
        # Unbind any stale context for debug purposes.
        self.doneCurrent()

        mb = MOUSE_BUTTONS.get(event.button())
        if mb is None:
            return

        pos = event.position()
        y = self.ctx.ctx_h - pos.y()
        self.ctx._handle_mouse_button_callback(
            pos.x(), y, mb, constants.MOUSE_BUTTON_PRESS, 0)

    def mouseReleaseEvent(self, event):
        # Unbind any stale context for debug purposes.
        self.doneCurrent()

        mb = MOUSE_BUTTONS.get(event.button())
        if mb is None:
            return

        pos = event.position()
        y = self.ctx.ctx_h - pos.y()
        self.ctx._handle_mouse_button_callback(
            pos.x(), y, mb, constants.MOUSE_BUTTON_RELEASE, 0)

    def mouseMoveEvent(self, event):
        # Unbind any stale context for debug purposes.
        self.doneCurrent()

        pos = event.position()
        y = self.ctx.ctx_h - pos.y()
        self.ctx._handle_mouse_moved(pos.x(), y)

    def wheelEvent(self, event):
        # Unbind any stale context for debug purposes.
        self.doneCurrent()

        delta = event.angleDelta()
        dx = delta.x() / 15.
        dy = delta.y() / 15.
        pos = event.position()
        y = self.ctx.ctx_h - pos.y()
        self.ctx._handle_mouse_scrolled(pos.x(), y, dx, dy)

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.KeypadModifier:
            key = PYSIDE_KEYPAD_KEYS.get(event.key())
        else:
            key = PYSIDE_KEYMAP_TO_GLOTLIB.get(event.key())
        if key is None:
            return

        self.ctx._handle_key_event(self.ctx.mouse_x, self.ctx.mouse_y, key,
                                   constants.KEY_PRESS)

    def keyReleaseEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.KeypadModifier:
            key = PYSIDE_KEYPAD_KEYS.get(event.key())
        else:
            key = PYSIDE_KEYMAP_TO_GLOTLIB.get(event.key())
        if key is None:
            return

        self.ctx._handle_key_event(self.ctx.mouse_x, self.ctx.mouse_y, key,
                                   constants.KEY_RELEASE)
