from autobahn.twisted.wamp import Application

app = Application()


# Let's create a WAMP application component that can square numbers
@app.register('com.examples.square')
def square(x):
    print("square() called with {}".format(x))
    return x * x


if __name__ == "__main__":
    app.run("ws://localhost:9000", "realm1", standalone=True)
