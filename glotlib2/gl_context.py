from OpenGL import GL


class GLContext:
    def __init__(self, msaa=None):
        self.opengl_context = None
        self.msaa = msaa

    def is_active(self):
        '''
        Returns true if we are bound to the current thread's OpenGL context.
        '''
        raise NotImplementedError

    def _init_gl(self, opengl_context):
        '''
        Called by the native window manager (or whatever is creating contexts)
        with the context bound to the current thread.  This is where you should
        initialize OpenGL state.
        '''
        self.opengl_context = opengl_context
        assert self.is_active()

        if self.msaa is not None:
            GL.glEnable(GL.GL_MULTISAMPLE)

        GL.glClearColor(1.0, 0.0, 0.0, 1.0)

    def _resize_gl_ctx(self, w, h):
        '''
        Called by the native window manager when the OpenGL context changes
        size.  The values are dimensions in window manager context coordinates.
        '''
        assert self.is_active()
        print('Context Resize: %u x %u' % (w, h))

    def _resize_gl_fb(self, w, h):
        '''
        Called by the native window manager when the OpenGL framebuffer changes
        size.  The values are the dimensions in framebuffer coordinates and
        take into count things like a Retina display which has twice as many
        pixels in each dimension compares to the window manager coordinates.
        '''
        assert self.is_active()
        print('Framebuffer Resize: %u x %u' % (w, h))

    def _paint_gl(self):
        '''
        This is called when the OS has decided that the window needs to be
        redrawn, for instance due to a window resize event.  We must always
        repaint the window since everything should be considered invalidated.
        '''
        assert self.is_active()
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
