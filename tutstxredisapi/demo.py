from __future__ import print_function

import txredisapi as redis

from twisted.internet import defer
from twisted.internet import reactor


@defer.inlineCallbacks
def main():
    rc = yield redis.Connection()
    print(rc)

    yield rc.set("foo", "bar")
    v = yield rc.get("foo")
    print("foo:", repr(v))

    yield rc.disconnect()


if __name__ == "__main__":
    main().addCallback(lambda ign: reactor.stop())
    reactor.run()