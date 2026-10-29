import threading
from collections import deque
from functools import partial


class EventQueue:
    '''
    Class to defer function calls to a later time.
    '''
    def __init__(self):
        self.lock = threading.Lock()
        self.queue = deque()

    def enqueue(self, func, *args, **kwargs):
        deferred_call = partial(func, *args, **kwargs)
        with self.lock:
            self.queue.append(deferred_call)

    def process(self):
        if not self.queue:
            return

        with self.lock:
            local_queue = self.queue
            self.queue = deque()

        for deferred_call in local_queue:
            deferred_call()
