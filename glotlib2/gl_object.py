import threading


class GLObjectMeta(type):
    '''
    Metaclass that causes the object to automatically be registered for deferred
    object notifications:

        _init_gl()
        _handle_resize()
    '''
    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        obj.gl_parent._register_new_gl_object(obj)
        return obj


class GLObject(metaclass=GLObjectMeta):
    def __init__(self, gl_parent):
        self.gl_parent = gl_parent

    def _init_gl(self):
        pass

    def _handle_resize(self):
        pass

    def _draw(self):
        pass


class GLParent:
    def __init__(self):
        self.gl_objects_lock = threading.Lock()
        self.new_gl_objects = []
        self.gl_objects = []

    def _register_new_gl_object(self, label):
        with self.gl_objects_lock:
            self.new_gl_objects.append(label)
        self.mark_dirty()

    def _init_new_gl_objects(self):
        '''
        Pops all GL objects from the new_gl_objects list, inits them and then
        adds them to the regular objects list.
        '''
        if self.new_gl_objects:
            with self.gl_objects_lock:
                new_gl_objects = self.new_gl_objects
                self.new_gl_objects = []

            for obj in new_gl_objects:
                obj._init_gl()
                self.gl_objects.append(obj)

    def mark_dirty(self):
        raise NotImplementedError
