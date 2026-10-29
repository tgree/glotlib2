import threading


class DeferredCall:
    def __init__(self, func, *args, **kwargs):
        self.func   = func
        self.args   = args
        self.kwargs = kwargs

    def handle_event(self, _owner):
        self.func(*self.args, **self.kwargs)


class EventQueue:
    '''
    Class to defer events to a later time.
    '''
    def __init__(self, owner):
        self.owner = owner
        self.lock  = threading.Lock()
        self.queue = []

    def enqueue(self, event):
        with self.lock:
            self.queue.append(event)

    def enqueue_call(self, func, *args, **kwargs):
        self.enqueue(DeferredCall(func, *args, **kwargs))

    def process(self):
        if not self.queue:
            return

        with self.lock:
            queue = self.queue
            self.queue = []

        for e in queue:
            e.handle_event(self.owner)
