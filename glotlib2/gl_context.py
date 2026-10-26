import threading

from OpenGL import GL

from .programs import Programs
from .faces import Faces
from .label import FlexLabel
from . import matrix


class GLContext:
    def __init__(self, msaa=None):
        self.opengl_context = None
        self.msaa = msaa
        self.programs = Programs()
        self.faces = Faces()

        self.ctx_w = None
        self.ctx_h = None
        self.fb_w  = None
        self.fb_h  = None
        self.mvp   = None

        self.labels_lock = threading.Lock()
        self.new_labels = []
        self.labels = []

    def is_active(self):
        '''
        Returns true if we are bound to the current thread's OpenGL context.
        '''
        raise NotImplementedError

    def mark_dirty(self):
        '''
        Marks the context as dirty so that the next time through the event loop
        a redraw will be forced.
        '''
        raise NotImplementedError

    def _init_new_labels(self):
        '''
        Pops all labels from the new_labels list, inits them and then adds them
        to the regular labels list.
        '''
        if self.new_labels:
            with self.labels_lock:
                new_labels = self.new_labels
                self.new_labels = []

            for l in new_labels:
                l._init_gl()
                self.labels.append(l)

    def _init_gl(self, opengl_context, ctx_w, ctx_h, fb_w, fb_h):
        '''
        Called by the native window manager (or whatever is creating contexts)
        with the context bound to the current thread.  This is where you should
        initialize OpenGL state.
        '''
        self.opengl_context = opengl_context
        assert self.is_active()

        self.ctx_w, self.ctx_h = ctx_w, ctx_h
        self.fb_w, self.fb_h = fb_w, fb_h
        self.mvp = matrix.ortho(0, self.ctx_w, 0, self.ctx_h, -1, 1)

        self.programs.load()

        if self.msaa is not None:
            GL.glEnable(GL.GL_MULTISAMPLE)

        GL.glClearColor(1.0, 0.0, 0.0, 1.0)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

    def _resize_gl_ctx(self, w, h):
        '''
        Called by the native window manager when the OpenGL context changes
        size.  The values are dimensions in window manager context coordinates.
        '''
        assert self.is_active()
        print('Context Resize: %u x %u' % (w, h))
        self.ctx_w, self.ctx_h = w, h
        self.mvp = matrix.ortho(0, self.ctx_w, 0, self.ctx_h, -1, 1)
        for l in self.labels:
            l._handle_resize()

    def _resize_gl_fb(self, w, h):
        '''
        Called by the native window manager when the OpenGL framebuffer changes
        size.  The values are the dimensions in framebuffer coordinates and
        take into count things like a Retina display which has twice as many
        pixels in each dimension compares to the window manager coordinates.
        '''
        assert self.is_active()
        print('Framebuffer Resize: %u x %u' % (w, h))
        self.fb_w, self.fb_h = w, h

    def _paint_gl(self):
        '''
        This is called when the OS has decided that the window needs to be
        redrawn, for instance due to a window resize event.  We must always
        repaint the window since everything should be considered invalidated.
        '''
        assert self.is_active()
        self._init_new_labels()
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        for l in self.labels:
            if l.visible:
                l.draw(self.mvp)

    def add_label(self, *args, face=None, font_size=12, **kwargs):
        face = face or self.faces.vera
        return FlexLabel(self, *args, face=face, font_size=font_size, **kwargs)

    def _register_new_label(self, label):
        with self.labels_lock:
            self.new_labels.append(label)
        self.mark_dirty()
