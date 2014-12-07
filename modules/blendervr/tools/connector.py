## copyright (C) LIMSI-CNRS (2014)
##
## contributor(s) : Jorge Gascon, Damien Touraine, David Poirier-Quinot,
## Laurent Pointal, Julian Adenauer, 
## 
## This software is a computer program whose purpose is to distribute
## blender to render on Virtual Reality device systems.
## 
## This software is governed by the CeCILL  license under French law and
## abiding by the rules of distribution of free software.  You can  use, 
## modify and/ or redistribute the software under the terms of the CeCILL
## license as circulated by CEA, CNRS and INRIA at the following URL
## "http://www.cecill.info". 
## 
## As a counterpart to the access to the source code and  rights to copy,
## modify and redistribute granted by the license, users are provided only
## with a limited warranty  and the software's author,  the holder of the
## economic rights,  and the successive licensors  have only  limited
## liability. 
## 
## In this respect, the user's attention is drawn to the risks associated
## with loading,  using,  modifying and/or developing or reproducing the
## software by the user in light of its specific status of free software,
## that may mean  that it is complicated to manipulate,  and  that  also
## therefore means  that it is reserved for developers  and  experienced
## professionals having in-depth computer knowledge. Users are therefore
## encouraged to load and test the software's suitability as regards their
## requirements in conditions enabling the security of their systems and/or 
## data to be ensured and,  more generally, to use and operate it in the 
## same conditions as regards security. 
## 
## The fact that you are presently reading this means that you have had
## knowledge of the CeCILL license and that you accept its terms.
## 

import socket
import select
from . import protocol

class Common:

    SIZE_LEN        = 10
    BUFFER_LEN      = 1024

    def __init__(self):
        self._socket     = None
        self._callback   = None
        self._buffers    = []
        self._initBuffer()
        self.setWait(True)

    def _initBuffer(self):
        if hasattr(self, '_buffer') and (len(self._buffer) > 0):
            self._buffers.append(self._buffer.decode())
        self._size   = 0
        self._buffer = b''

    def __del__(self):
        self.close()

    def setCallback(self, callback):
        self._callback = callback
        self._flushBuffers()

    def _flushBuffers(self):
        if len(self._buffers) and self._callback:
            while len(self._buffers) > 0:
                buffer = self._buffers.pop(0)
                self._callback(*protocol.decomposeMessage(buffer))

    def setSocket(self, _socket, callback = None):
        self.close()
        self._socket = _socket
        self._socket.setblocking(0)

    def getSocket(self):
        return self._socket

    def send(self, command, argument = ''):
        if self._socket is None:
            return
        message = protocol.composeMessage(command, argument)
        size = str(len(message)).zfill(self.SIZE_LEN)
        self._send_chunk(size.encode())
        while len(message) > 0:
            buffer = message[:self.BUFFER_LEN]
            message = message[self.BUFFER_LEN:]
            self._send_chunk(buffer.encode())

    # Be carefull: we use non blocking socket. So, we must wait for the buffer to be empty before sending elements ...
    def _send_chunk(self, data):
        total_send = 0
        while total_send < len(data):
            select.select([], [self._socket], [])
            sent = self._socket.send(data[total_send:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            total_send += sent

    def close(self):
        if self._socket:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
                self._socket.close()
            except:
                pass
            self._socket = None

    def fileno(self):
        if self._socket:
            return self._socket.fileno()
        return None

    def setWait(self, block):
        if block:
            self._timeoutSelect = None
        else:
            self._timeoutSelect = 0

    def run(self):
        while True:
            if self._socket is None:
                return False

            inputready, outputready, exceptready = select.select([self._socket], [], [], self._timeoutSelect)

            if self._socket not in inputready:
                return True

            if self._size == 0:
                data_size = self.SIZE_LEN
            else:
                data_size = self._size - len(self._buffer)

            try:
                data = self._socket.recv(data_size)
            except:
                data = False
            if not data:
                self.close()
                return False

            if self._size == 0:
                self._size = int(data)
            else:
                self._buffer += data
                if len(self._buffer) == self._size:
                    self._initBuffer()
                    self._flushBuffers()
                    

class Client(Common):
    def __init__(self, controller, module, complement = ''):
        Common.__init__(self)

        if isinstance(controller, str):
            controller = controller.split(':')
            controller[1] = int(controller[1])
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.connect(tuple(controller))

        self.setSocket(_socket)

        self.send(module, complement)

class Server(Common):
    def __init__(self, _socket):
        Common.__init__(self)
        self.setSocket(_socket)
        self.setCallback(self._receiveClientInformation)
        self.setWait(True)
        while not hasattr(self, '_complement'):
            self.run()

    def _receiveClientInformation(self, module, complement):
        self._module     = module
        self._complement = complement
        self.setCallback(None)
        self.setWait(False)

    def getClientInformation(self):
        return (self._module, self._complement)

class Listener:
    def __init__(self, client_processor):
        self._clients = {}

        self._server  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._port    = 31415
        while True:
            try:
                self._server.bind(('', self._port))
                break
            except socket.error:
                self._port += 1

        self._server.listen(100)
        self.addCallback(self._server.fileno(), self._connect_client)
        self._client_processor = client_processor

    def select(self):
        inputready, outputready, exceptready = select.select(self._clients.keys(), [], [])
        for sock in inputready:
            if sock in self._clients:
                if not self._clients[sock]():
                    del(self._clients[sock])

    def _connect_client(self):
        conn, addr = self._server.accept()

        from ..tools.connector import Server
        client = Server(conn)

        self._client_processor(client.getClientInformation())
        return True
        
    def getPort(self):
        return self._port

    def addCallback(self, socket, callback):
        if isinstance(client, Common):
            socket = client.getSocket()
        elif isinstance(client, int):
            socket = client
        else:
            return False
        self._clients[socket] = callback
        return True

    def delCallback(self, socket):
        if isinstance(client, Common):
            self._clients[client.getSocket()] = callback
        elif isinstance(client, int):
            self._clients[client.getSocket()] = callback
        if socket in self._clients:
            del(self._clients[socket])
        
                
        
