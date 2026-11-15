import time
import threading
from functools import partial


class Ticker:
    '''
    Periodically calls the specified function.
    '''
    def __init__(self, interval, func, *args, **kwargs):
        self.deferred_call = partial(func, *args, **kwargs)
        self.interval = interval
        self.thread = threading.Thread(target=self.ticker_loop, daemon=True)
        self.thread.start()

    def ticker_loop(self):
        next_deadline = time.monotonic()
        while True:
            next_deadline += self.interval

            self.deferred_call()

            now = time.monotonic()
            if next_deadline >= now:
                time.sleep(next_deadline - now)
            else:
                next_deadline = now
