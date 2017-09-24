from bisect import insort
from collections import namedtuple
from functools import wraps
from time import time
import selectors2 as selectors
import sys

Timer = namedtuple('Timer', ['timestamp', 'handler'])


def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time()
        return_value = func(*args, **kwargs)
        message = "Executing {} took {:.03} seconds.".format(func.__name__,
                                                             time() - start)
        print(message)
        return return_value

    return wrapper


def fib(n):
    return fib(n - 1) + fib(n - 2) if n > 1 else n


timed_fib = log_execution_time(fib)


def on_stdin_input(line):
    if line == 'exit':
        loop.stop()
        return
    n = int(line)
    print("fib({}) = {}".format(n, timed_fib(n)))


def print_hello():
    print("{} - Hello world!".format(int(time())))
    loop.add_timer(3, print_hello)


class EventLoop(object):
    """
    Implements a callback based single-threaded event loop as a simple
    demonstration.
    """
    def __init__(self, *args, **kwargs):
        self._running = False
        self._stdin_handlers = []
        self._timers = []
        self._selector = selectors.DefaultSelector()
        self._selector.register(sys.stdin, selectors.EVENT_READ)

    def run_forever(self):
        self._running = True
        while self._running:
            # First check for available IO input
            for key, mask in self._selector.select(0):
                line = key.fileobj.readline().strip()
                for callback in self._stdin_handlers:
                    callback(line)

            # Handle timer events
            while self._timers and self._timers[0].timestamp < time():
                handler = self._timers[0].handler
                del self._timers[0]
                handler()

    def add_stdin_handler(self, callback):
        self._stdin_handlers.append(callback)

    def add_timer(self, wait_time, callback):
        timer = Timer(timestamp=time() + wait_time, handler=callback)
        insort(self._timers, timer)

    def stop(self):
        self._running = False


if __name__ == '__main__':
    try:
        loop = EventLoop()
        loop.add_stdin_handler(on_stdin_input)
        loop.add_timer(0, print_hello)
        loop.run_forever()
    except KeyboardInterrupt as e:
        pass
