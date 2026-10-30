import os
import ctypes

import glfw
from OpenGL import GL

from .gl_context import GLContext
from .backend import _register_window
from .. import constants


MOUSE_ACTIONS = {
    glfw.PRESS      : constants.MOUSE_BUTTON_PRESS,
    glfw.RELEASE    : constants.MOUSE_BUTTON_RELEASE,
}

MOUSE_BUTTONS = {
    glfw.MOUSE_BUTTON_LEFT   : constants.MOUSE_BUTTON_LEFT,
    glfw.MOUSE_BUTTON_RIGHT  : constants.MOUSE_BUTTON_RIGHT,
    glfw.MOUSE_BUTTON_MIDDLE : constants.MOUSE_BUTTON_MIDDLE,
    glfw.MOUSE_BUTTON_4      : None,
    glfw.MOUSE_BUTTON_5      : None,
    glfw.MOUSE_BUTTON_6      : None,
    glfw.MOUSE_BUTTON_7      : None,
    glfw.MOUSE_BUTTON_8      : None,
}

KEY_ACTIONS = {
    glfw.PRESS      : constants.KEY_PRESS,
    glfw.RELEASE    : constants.KEY_RELEASE,
}

GLFW_KEYMAP_TO_GLOTLIB = {
    glfw.KEY_A              : 'a',
    glfw.KEY_B              : 'b',
    glfw.KEY_C              : 'c',
    glfw.KEY_D              : 'd',
    glfw.KEY_E              : 'e',
    glfw.KEY_F              : 'f',
    glfw.KEY_G              : 'g',
    glfw.KEY_H              : 'h',
    glfw.KEY_I              : 'i',
    glfw.KEY_J              : 'j',
    glfw.KEY_K              : 'k',
    glfw.KEY_L              : 'l',
    glfw.KEY_M              : 'm',
    glfw.KEY_N              : 'n',
    glfw.KEY_O              : 'o',
    glfw.KEY_P              : 'p',
    glfw.KEY_Q              : 'q',
    glfw.KEY_R              : 'r',
    glfw.KEY_S              : 's',
    glfw.KEY_T              : 't',
    glfw.KEY_U              : 'u',
    glfw.KEY_V              : 'v',
    glfw.KEY_W              : 'w',
    glfw.KEY_X              : 'x',
    glfw.KEY_Y              : 'y',
    glfw.KEY_Z              : 'z',
    glfw.KEY_0              : '0',
    glfw.KEY_1              : '1',
    glfw.KEY_2              : '2',
    glfw.KEY_3              : '3',
    glfw.KEY_4              : '4',
    glfw.KEY_5              : '5',
    glfw.KEY_6              : '6',
    glfw.KEY_7              : '7',
    glfw.KEY_8              : '8',
    glfw.KEY_9              : '9',
    glfw.KEY_SPACE          : ' ',
    glfw.KEY_ENTER          : '\r',
    glfw.KEY_ESCAPE         : constants.KEY_ESCAPE,
    glfw.KEY_BACKSPACE      : '\b',
    glfw.KEY_DELETE         : constants.KEY_DELETE,
    glfw.KEY_TAB            : '\t',
    glfw.KEY_UP             : constants.KEY_UP_ARROW,
    glfw.KEY_DOWN           : constants.KEY_DOWN_ARROW,
    glfw.KEY_LEFT           : constants.KEY_LEFT_ARROW,
    glfw.KEY_RIGHT          : constants.KEY_RIGHT_ARROW,
    glfw.KEY_PAGE_UP        : constants.KEY_PAGE_UP,
    glfw.KEY_PAGE_DOWN      : constants.KEY_PAGE_DOWN,
    glfw.KEY_HOME           : constants.KEY_HOME,
    glfw.KEY_END            : constants.KEY_END,
    glfw.KEY_LEFT_SHIFT     : constants.KEY_LEFT_SHIFT,
    glfw.KEY_RIGHT_SHIFT    : constants.KEY_RIGHT_SHIFT,
    glfw.KEY_LEFT_CONTROL   : constants.KEY_LEFT_CONTROL,
    glfw.KEY_RIGHT_CONTROL  : constants.KEY_RIGHT_CONTROL,
    glfw.KEY_LEFT_ALT       : constants.KEY_LEFT_ALT,
    glfw.KEY_RIGHT_ALT      : constants.KEY_RIGHT_ALT,
    glfw.KEY_LEFT_SUPER     : constants.KEY_LEFT_SUPER,     # macOS Command
    glfw.KEY_RIGHT_SUPER    : constants.KEY_RIGHT_SUPER,    # macOS Command
    glfw.KEY_GRAVE_ACCENT   : '`',
    glfw.KEY_APOSTROPHE     : "'",
    glfw.KEY_MINUS          : '-',
    glfw.KEY_EQUAL          : '=',
    glfw.KEY_LEFT_BRACKET   : '[',
    glfw.KEY_RIGHT_BRACKET  : ']',
    glfw.KEY_SEMICOLON      : ':',
    glfw.KEY_BACKSLASH      : '\\',
    glfw.KEY_COMMA          : ',',
    glfw.KEY_PERIOD         : '.',
    glfw.KEY_SLASH          : '/',

    glfw.KEY_KP_0           : constants.KEYPAD_0,
    glfw.KEY_KP_1           : constants.KEYPAD_1,
    glfw.KEY_KP_2           : constants.KEYPAD_2,
    glfw.KEY_KP_3           : constants.KEYPAD_3,
    glfw.KEY_KP_4           : constants.KEYPAD_4,
    glfw.KEY_KP_5           : constants.KEYPAD_5,
    glfw.KEY_KP_6           : constants.KEYPAD_6,
    glfw.KEY_KP_7           : constants.KEYPAD_7,
    glfw.KEY_KP_8           : constants.KEYPAD_8,
    glfw.KEY_KP_9           : constants.KEYPAD_9,
    glfw.KEY_KP_DECIMAL     : constants.KEYPAD_DOT,
    glfw.KEY_KP_DIVIDE      : constants.KEYPAD_DIVIDE,
    glfw.KEY_KP_MULTIPLY    : constants.KEYPAD_MULTIPLY,
    glfw.KEY_KP_SUBTRACT    : constants.KEYPAD_MINUS,
    glfw.KEY_KP_ADD         : constants.KEYPAD_PLUS,
    glfw.KEY_KP_EQUAL       : constants.KEYPAD_EQUALS,
    glfw.KEY_KP_ENTER       : constants.KEYPAD_ENTER,

    glfw.KEY_CAPS_LOCK      : constants.KEY_CAPS_LOCK,
    glfw.KEY_F1             : constants.KEY_F1,
    glfw.KEY_F2             : constants.KEY_F2,
    glfw.KEY_F3             : constants.KEY_F3,
    glfw.KEY_F4             : constants.KEY_F4,
    glfw.KEY_F5             : constants.KEY_F5,
    glfw.KEY_F6             : constants.KEY_F6,
    glfw.KEY_F7             : constants.KEY_F7,
    glfw.KEY_F8             : constants.KEY_F8,
    glfw.KEY_F9             : constants.KEY_F9,
    glfw.KEY_F10            : constants.KEY_F10,
    glfw.KEY_F11            : constants.KEY_F11,
    glfw.KEY_F12            : constants.KEY_F12,
    glfw.KEY_F13            : constants.KEY_F13,
    glfw.KEY_F14            : constants.KEY_F14,
    glfw.KEY_F15            : constants.KEY_F15,
    glfw.KEY_F16            : constants.KEY_F16,
    glfw.KEY_F17            : constants.KEY_F17,
    glfw.KEY_F18            : constants.KEY_F18,
    glfw.KEY_F19            : constants.KEY_F19,
    glfw.KEY_F20            : constants.KEY_F20,
    glfw.KEY_F21            : constants.KEY_F21,
    glfw.KEY_F22            : constants.KEY_F22,
    glfw.KEY_F23            : constants.KEY_F23,
    glfw.KEY_F24            : constants.KEY_F24,
    glfw.KEY_F25            : constants.KEY_F25,
    glfw.KEY_INSERT         : constants.KEY_INSERT,
    glfw.KEY_MENU           : constants.KEY_MENU,
    glfw.KEY_NUM_LOCK       : constants.KEY_NUM_LOCK,
    glfw.KEY_PAUSE          : constants.KEY_PAUSE,
    glfw.KEY_PRINT_SCREEN   : constants.KEY_PRINT_SCREEN,
    glfw.KEY_SCROLL_LOCK    : constants.KEY_SCROLL_LOCK,
    glfw.KEY_UNKNOWN        : None,
}

GLOTLIB_KEYMAP_TO_GLFW = {v: k for k, v in GLFW_KEYMAP_TO_GLOTLIB.items()}


class Window:
    def __init__(self, w, h, x=100, y=100, name='', msaa=None, delegate=None):
        self.glfw_window = glfw.create_window(w, h, name, None, None)
        glfw.set_window_pos(self.glfw_window, x, y)
        glfw.set_window_size_limits(self.glfw_window, 16, 16,
                                    glfw.DONT_CARE, glfw.DONT_CARE)

        glfw.set_window_size_callback(
            self.glfw_window, self._handle_window_size_changed)
        glfw.set_framebuffer_size_callback(
            self.glfw_window, self._handle_framebuffer_size_changed)
        glfw.set_window_iconify_callback(
            self.glfw_window, self._handle_window_iconified)
        glfw.set_window_refresh_callback(
            self.glfw_window, self._handle_window_refresh)
        glfw.set_cursor_pos_callback(
            self.glfw_window, self._handle_mouse_moved)
        glfw.set_mouse_button_callback(
            self.glfw_window, self._handle_mouse_button_callback)
        glfw.set_scroll_callback(
            self.glfw_window, self._handle_mouse_scrolled)
        glfw.set_key_callback(
            self.glfw_window, self._handle_key_event)

        self._iconified = False
        self.ctx = GLContext(self.glfw_window, msaa=msaa, delegate=delegate)

        glfw.make_context_current(self.glfw_window)
        profile_mask = GL.glGetIntegerv(GL.GL_CONTEXT_PROFILE_MASK)
        is_core_profile = bool(profile_mask & GL.GL_CONTEXT_CORE_PROFILE_BIT)
        if not is_core_profile:
            print('GLOTLIB ERROR: Failed to secure Core Profile. '
                  'Did you call glotlib.glfw.init_backend()?')
            os._exit(-1)

        current_context = glfw.get_current_context()
        assert current_context is not None
        ctx_w, ctx_h = glfw.get_window_size(self.glfw_window)
        fb_w, fb_h = glfw.get_framebuffer_size(self.glfw_window)
        self.ctx._init_ctx(ctypes.cast(current_context, ctypes.c_void_p).value,
                           ctx_w, ctx_h, fb_w, fb_h)
        self.ctx._tree_resize_gl_ctx(ctx_w, ctx_h)
        self.ctx._tree_resize_gl_fb(fb_w, fb_h)

        _register_window(self)

    def _should_close(self):
        return glfw.window_should_close(self.glfw_window)

    def _destroy(self):
        glfw.destroy_window(self.glfw_window)

    def _swap_buffers(self):
        glfw.swap_buffers(self.glfw_window)

    def _handle_window_size_changed(self, _window, w, h):
        # This always seems to fire second.
        if not self._iconified:
            self.ctx._tree_resize_gl_ctx(w, h)

    def _handle_framebuffer_size_changed(self, _window, w, h):
        # This always seems to fire first.
        if not self._iconified:
            self.ctx._tree_resize_gl_fb(w, h)

    def _handle_window_iconified(self, _window, iconified):
        self._iconified = iconified

    def _handle_window_refresh(self, _window):
        '''
        This is called when the OS has decided that the window needs to be
        redrawn, for instance due to a window resize event.  We must always
        repaint the window since everything should be considered invalidated.
        '''
        self.ctx._tree_paint_gl()
        self._swap_buffers()

    def _handle_mouse_moved(self, _window, x, y):
        y = self.ctx.ctx_h - y
        self.ctx._handle_mouse_moved(x, y)

    def _handle_mouse_button_callback(self, _window, button, action, mods):
        mb = MOUSE_BUTTONS.get(button)
        if mb is None:
            return

        action = MOUSE_ACTIONS.get(action)
        if action is None:
            return

        self.ctx._handle_mouse_button_callback(self.ctx.mouse_x,
                                               self.ctx.mouse_y, mb, action,
                                               mods)

    def _handle_mouse_scrolled(self, _window, dx, dy):
        self.ctx._handle_mouse_scrolled(self.ctx.mouse_x, self.ctx.mouse_y,
                                        dx, dy)

    def _handle_key_event(self, _window, key, _scancode, action, _mods):
        action = KEY_ACTIONS.get(action)
        if action is None:
            return

        key = GLFW_KEYMAP_TO_GLOTLIB.get(key)
        if key is None:
            return

        self.ctx._handle_key_event(self.ctx.mouse_x, self.ctx.mouse_y, key,
                                   action)
