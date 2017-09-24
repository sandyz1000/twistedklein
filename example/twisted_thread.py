from __future__ import print_function

import time
from twisted.internet import reactor
from twisted.internet import threads
from twisted.python import threadable
from twisted.web.client import getPage
from twisted.web.error import Error

threadable.init()


def not_thread_safe(x):
    """
    but not_thread_safe should only ever be called by code running in the
    thread where reactor.run is running.
    """
    print("Sleep for 2 sec")
    time.sleep(2)
    print(x)


def thread_safe_scheduler():
    """Run in thread-safe manner."""
    # will run 'notThreadSafe(3)' in the event loop
    # Most code in Twisted is not thread-safe. For example, writing data to a transport from a
    # protocol is not thread-safe. Therefore, we want a way to schedule methods to be run in
    # the main event loop.

    reactor.callFromThread(not_thread_safe, 3)


# Running code in threads
# Sometimes we may want to run methods in threads - for example, in order to access
# blocking APIs. Twisted provides methods for doing so using the IReactorThreads API

def a_silly_blocking_method(x):
    print("Sleep for 2 sec")
    time.sleep(2)
    print(x)


# run method in thread
# callInThread will put your code into a queue, to be run by the next available thread in the
# reactor's thread pool.

reactor.callInThread(a_silly_blocking_method, "2 seconds have passed")


# Utility Methods
# If we have multiple methods to run sequentially within a thread, we can do:
def a_silly_blocking_method_one(x):
    print("Sleep for 2 sec")
    time.sleep(2)
    print(x)


def a_silly_blocking_method_two(x):
    print(x)


# run both methods sequentially in a thread
commands = [(a_silly_blocking_method_one, ["Calling First"], {}),
            (a_silly_blocking_method_two, ["And the second"], {})]


threads.callMultipleInThread(commands)


# For functions whose results we wish to get, we can have the result returned as a Deferred:
def do_long_calculation(x):
    # .... do long calculation here ...
    print("Sleep for 3 sec")
    time.sleep(3)
    return x


def print_failed(err):
    print('Error occurred')


def print_result(x):
    print(x)
    reactor.stop()


# run method in thread and get result as defer.Deferred
d = threads.deferToThread(do_long_calculation, 3)
d.addCallbacks(print_result, print_failed)


def inThread():
    try:
        result = threads.blockingCallFromThread(reactor, getPage, "http://twistedmatrix.com/")
    except Error as exc:
        print(exc)
    else:
        print(result)
    reactor.callFromThread(reactor.stop)

reactor.callInThread(inThread)

# The thread pool is implemented by twisted.python.threadpool.ThreadPool.
# We may want to modify the size of the threadpool, increasing or decreasing the number of
# threads in use. We can do this do this quite easily:

# The size of the thread pool defaults to a maximum of 10 threads. Be careful that you understand
# threads and their resource usage before drastically altering the thread pool sizes.

reactor.suggestThreadPoolSize(20)


reactor.run()