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

class closedSocket(Exception):
    def __init__(self):
        Exception.__init__(self, 'Socket closed in the meantime')

class Common:

    SIZE_LEN        = 10
    BUFFER_LEN      = 1024

    def __init__(self):
        self._socket     = None

    def _initBuffer(self):
        if hasattr(self, '_buffer') and (len(self._buffer) > 0):
            self._buffers.append(self._buffer.decode())
        self._size   = 0
        self._buffer = b''

    def __del__(self):
        self.close()

    def setSocket(self, _socket):
        self.close()
        self._socket = _socket

    def getSocket(self):
        return self._socket

    def fileno(self):
        if self._socket:
            return self._socket.fileno()
        return None

    def send(self, command, argument = ''):
        if self._socket is None:
            return
        message = protocol.composeMessage(command, argument)
        size = str(len(message)).zfill(self.SIZE_LEN)
        try:
            self._send_chunk(size.encode())
            while len(message) > 0:
                buffer = message[:self.BUFFER_LEN]
                message = message[self.BUFFER_LEN:]
                self._send_chunk(buffer.encode())
        except:
            self.close()
            raise

    def _send_chunk(self, data):
        total_send = 0
        while total_send < len(data):
            select.select([], [self._socket], [])
            sent = self._socket.send(data[total_send:])
            if sent == 0:
                raise closedSocket()
            total_send += sent

    def receive(self, block = True):
        if self._socket is None:
            return False
        if not block:
            inputready, outputready, exceptready = select.select([self._socket], [], [], 0)
            if self._socket not in inputready:
                return False
        try:
            size = int(self._receive_chunk(self.SIZE_LEN))
            return protocol.decomposeMessage(self._receive_chunk(size))
        except closedSocket:
            self.close()
            raise
        return False

    def _receive_chunk(self, size):
        data = b''
        while len(data) < size:
            data_chunk = self._socket.recv(size)
            if not data_chunk:
                raise closedSocket()
            data += data_chunk
        return data.decode()

    def close(self):
        if self._socket:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
                self._socket.close()
            except:
                pass
        self._socket = None
        
class Controller(Common):
    def __init__(self, controller, module, complement = ''):
        Common.__init__(self)

        if isinstance(controller, str):
            controller = controller.split(':')
            controller[1] = int(controller[1])
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.connect(tuple(controller))

        self.setSocket(_socket)

        self.send(module, complement)
