import selectors2 as selectors
import sys
from time import time
from functools import wraps


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


def process_input(stream):
    text = stream.readline()
    n = int(text.strip())
    print('fib({}) = {}'.format(n, timed_fib(n)))


def print_hello():
    print("{} - Hello world!".format(int(time())))


if __name__ == '__main__':
    selector = selectors.DefaultSelector()
    # Register the selector to poll for "read" readiness on stdin
    selector.register(sys.stdin, selectors.EVENT_READ)
    last_hello = 0  # Setting to 0 means the timer will start right away

    try:
        while True:
            # Wait at most 100 milliseconds for input to be available
            for event, mask in selector.select(0.1):
                process_input(event.fileobj)

            if time() - last_hello > 3:
                last_hello = time()
                print_hello()
    except KeyboardInterrupt as e:
        pass