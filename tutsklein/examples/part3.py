from twisted.internet.defer import inlineCallbacks, returnValue
from klein import Klein
import treq
from autobahn.twisted.wamp import Application

app = Klein()
wampapp = Application()


@app.route('/square/submit', methods=['POST'])
@inlineCallbacks
def square_submit(request):
    x = int(request.args.get('x', [0])[0])
    res = yield wampapp.session.call('com.example.square', x)
    returnValue("{} squared is {}".format(x, res))


@app.route('/', branch=True)
def google(request):
    d = treq.get('https://www.google.com' + request.uri)
    d.addCallback(treq.content)
    return d


if __name__ == "__main__":
    import sys
    from twisted.python import log
    from twisted.web.server import Site
    from twisted.internet import reactor

    log.startLogging(sys.stdout)

    reactor.listenTCP(8080, Site(app.resource()))
    wampapp.run("ws://localhost:9000", "realm1", standalone=False)
