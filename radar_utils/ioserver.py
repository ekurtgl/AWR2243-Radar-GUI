from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from threading import Thread
# import os
#
# os.environ['WERKZEUG_RUN_MAIN'] = 'true'


class IOServer:

    def __init__(self):
        self.app = Flask(__name__)
        self.sio = SocketIO(
            self.app, cors_allowed_origins="*", async_mode='threading')

    def run(self):
        self.sio.run(self.app)

    def runDaemon(self):
        self.thread = Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def on(self, msg, handler):
        self.sio.on(msg)(handler)

    def send(self, msg, data):
        print("EMIT")
        print(data)
        self.sio.emit(msg, {'data': data})


'''
Usage Example
-------------

server = IOServer()

def onConnect():
    print('New Socket Connected')

def onDisconnect():
    print('Socket Disconnected')

def startStream(*args):
    import time, random
    while True:
        time.sleep(0.1)
        server.send('data', random.random() * 30)


server.on('connect', onConnect)
server.on('stream', startStream)
server.run()

'''
