#!/home/moozg/venvs/saf/bin/python3.5
#coding: utf-8
from .swss import SimpleWebSocketServer, WebSocket
from .settings import conf
from .log import logger

clients = set()


def broadcast_message(message):
    global socket_lock
    socket_lock.acquire()
    try:
        for client in clients:
            client.sendMessage(message)
    finally:
        socket_lock.release()


class SimpleNotifier(WebSocket):

    def handleMessage(self):
        self.sendMessage(self.data)
        logger.debug('message received:', repr(self.data[:32]) )

    def handleConnected(self):
        socket_lock.acquire()
        try:
            clients.add(self)
        finally:
            socket_lock.release()
        logger.debug('websocket client connected: %s:%i' % self.address )

    def handleClose(self):
        socket_lock.acquire()
        try:
            clients.discard(self)
        finally:
            socket_lock.release()
        logger.debug('websocket client connected  %s:%i' % self.address)


class PipeWebSocketServer(SimpleWebSocketServer):

    def __init__(self, pipe, *args, **kwargs):
        self.pipe = pipe
        kwargs['selectTimeout'] = 0.5
        super(PipeWebSocketServer, self).__init__(*args, **kwargs)

    def handle_pipe_message(self, data):
        broadcast_message(data)

    def _before_select(self):
        if not self.pipe.poll():
            return
        data = self.pipe.recv()
        self.handle_pipe_message(data)


def run_socket_server(socklock, pipe_recv):
    '''
    Run websocket server as daemon

    socklock - socket access semaphore
    pipe_recv - multiprocessing communication pipe, receiver side
    '''
    global SockServ, socket_lock
    socket_lock = socklock
    logger.info("Starting websocket server")
    logger.info("Listening on %s:%s" % (conf.WEBSOCKET_ADDRESS, conf.WEBSOCKET_PORT) )
    SockServ = PipeWebSocketServer(
        pipe_recv,
        conf.WEBSOCKET_ADDRESS, int(conf.WEBSOCKET_PORT),
        SimpleNotifier)
    try:
        SockServ.serveforever()
    except KeyboardInterrupt:
        pass
    logger.info("Stopping websocket server")
