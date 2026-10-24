import os
import ctypes

import glfw
from OpenGL import GL

from .gl_context import GLContext
from .backend import _register_window


class Window:
    def __init__(self, w, h, x=100, y=100, name='', msaa=None):
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

        self._iconified = False
        self.ctx = GLContext(msaa=msaa)

        glfw.make_context_current(self.glfw_window)
        profile_mask = GL.glGetIntegerv(GL.GL_CONTEXT_PROFILE_MASK)
        is_core_profile = bool(profile_mask & GL.GL_CONTEXT_CORE_PROFILE_BIT)
        if not is_core_profile:
            print('GLOTLIB ERROR: Failed to secure Core Profile. '
                  'Did you call glotlib.glfw.init_backend()?')
            os._exit(-1)

        current_context = glfw.get_current_context()
        assert current_context is not None
        self.ctx._init_gl(ctypes.cast(current_context, ctypes.c_void_p).value)

        ctx_w, ctx_h = glfw.get_window_size(self.glfw_window)
        self.ctx._resize_gl_ctx(ctx_w, ctx_h)

        fb_w, fb_h = glfw.get_framebuffer_size(self.glfw_window)
        self.ctx._resize_gl_fb(fb_w, fb_h)

        _register_window(self)

    def _should_close(self):
        return glfw.window_should_close(self.glfw_window)

    def _destroy(self):
        glfw.destroy_window(self.glfw_window)

    def _swap_buffers(self):
        glfw.swap_buffers(self.glfw_window)

    def _handle_window_size_changed(self, _window, w, h):
        if not self._iconified:
            self.ctx._resize_gl_ctx(w, h)

    def _handle_framebuffer_size_changed(self, _window, w, h):
        if not self._iconified:
            self.ctx._resize_gl_fb(w, h)

    def _handle_window_iconified(self, _window, iconified):
        self._iconified = iconified

    def _handle_window_refresh(self, _window):
        '''
        This is called when the OS has decided that the window needs to be
        redrawn, for instance due to a window resize event.  We must always
        repaint the window since everything should be considered invalidated.
        '''
        self.ctx._paint_gl()
        self._swap_buffers()
