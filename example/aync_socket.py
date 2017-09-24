"""

Module asyncore also supplies class 'dispatcher', which supplies all methods of socket objects,
plus specific methods for event-driven programming, with names starting with 'handle_'.
Your class X subclasses dispatcher and overrides the 'handle_' methods for all events you need to
handle.

To initialize an instance d of dispatcher, you can pass an argument s, an already connected
socket object.

Otherwise, you must call: d.create_socket(socket.AF_INET,socket.SOCK_STREAM)

and then call on d either connect, to connect to a server, or bind and listen, to have d itself
be a server. The most frequently used methods of an instance d of a subclass X of dispatcher are
the following.

"""

import select
import socket
import asyncore

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', 8881))
sock.listen(5)

# lists of sockets to watch for input and output events
ins = [sock]
ous = []
# mapping socket -> data to send on that socket when feasible
data = {}
# mapping socket -> (host, port) on which the client is running
adrs = {}


class MainServerSocket(asyncore.dispatcher):
    def __init__(self, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('', port))
        self.listen(5)

    def handle_accept(self):
        newSocket, address = self.accept()
        print("Connected from", address)
        SecondaryServerSocket(newSocket)


class SecondaryServerSocket(asyncore.dispatcher_with_send):
    def handle_read(self):
        receivedData = self.recv(8192)
        if receivedData:
            self.send(receivedData)
        else:
            self.close()

    def handle_close(self):
        print("Disconnected from", self.getpeername())


MainServerSocket(8881)
asyncore.loop()

try:
    while True:
        i, o, e = select.select(ins, ous, [])  # no excepts nor timeout
        for x in i:
            if x is sock:
                # input event on sock means client trying to connect
                newSocket, address = sock.accept()
                print("Connected from", address)
                ins.append(newSocket)
                adrs[newSocket] = address
            else:
                # other input events mean data arrived, or disconnections
                newdata = x.recv(8192)
                if newdata:
                    # data arrived, prepare and queue the response to it
                    print("%d bytes from %s" % (len(newdata), adrs[x]))
                    data[x] = data.get(x, '') + newdata
                    if x not in ous: ous.append(x)
                else:
                    # a disconnect, give a message and clean up
                    print("disconnected from", adrs[x])
                    del adrs[x]
                    try:
                        ous.remove(x)
                    except ValueError:
                        pass
                    x.close()
        for x in o:
            # output events always mean we can send some data
            tosend = data.get(x)
            if tosend:
                nsent = x.send(tosend)
                print("%d bytes to %s" % (nsent, adrs[x]))
                # remember data still to be sent, if any
                tosend = tosend[nsent:]
            if tosend:
                print("%d bytes remain for %s" % (len(tosend), adrs[x]))
                data[x] = tosend
            else:
                try:
                    del data[x]
                except KeyError:
                    pass
                ous.remove(x)
                print("No data currently remain for", adrs[x])
finally:
    sock.close()
