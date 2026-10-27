import threading


class GLObjectMeta(type):
    '''
    Metaclass that causes the object to automatically be registered with the
    parent.
    '''
    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        if obj.gl_parent:
            obj.gl_parent._tree_register_new_gl_child(obj)
        return obj


class GLObject(metaclass=GLObjectMeta):
    def __init__(self, gl_parent):
        self.gl_parent        = gl_parent
        self.gl_children_lock = threading.Lock()
        self.new_gl_children  = []
        self.gl_children      = []

        if gl_parent:
            self.ctx = getattr(gl_parent, 'ctx', gl_parent)

    def _init_gl(self):
        pass

    def _resize_gl_ctx(self, w, h):
        pass

    def _resize_gl_fb(self, w, h):
        pass

    def _paint_gl(self):
        pass

    def mark_dirty(self):
        '''
        Marks the context as dirty so that the next time through the event loop
        a redraw will be forced.
        '''
        self.gl_parent.mark_dirty()

    def _tree_register_new_gl_child(self, child):
        with self.gl_children_lock:
            self.new_gl_children.append(child)
        self.mark_dirty()

    def _tree_init_new_gl_children(self):
        '''
        Pops all GL objects from the new_gl_children list, inits them and then
        adds them to the regular objects list.
        '''
        if self.new_gl_children:
            with self.gl_children_lock:
                new_gl_children = self.new_gl_children
                self.new_gl_children = []

            for obj in new_gl_children:
                obj._init_gl()
                self.gl_children.append(obj)
                obj._tree_init_new_gl_children()

    def _tree_resize_gl_ctx(self, w, h):
        self._resize_gl_ctx(w, h)
        for obj in self.gl_children:
            obj._tree_resize_gl_ctx(w, h)

    def _tree_resize_gl_fb(self, w, h):
        self._resize_gl_fb(w, h)
        for obj in self.gl_children:
            obj._tree_resize_gl_fb(w, h)

    def _tree_paint_gl(self):
        self._tree_init_new_gl_children()
        self._paint_gl()
        for obj in self.gl_children:
            obj._tree_paint_gl()
