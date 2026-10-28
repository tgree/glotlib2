import threading


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

    def process(self):
        if not self.queue:
            return

        with self.lock:
            queue = self.queue
            self.queue = []

        for e in queue:
            e.handle_event(self.owner)
