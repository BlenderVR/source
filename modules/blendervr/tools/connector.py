## Copyright (C) LIMSI-CNRS (2014)
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
import json
import select

class Common:

    SIZE_LEN        = 10
    BUFFER_LEN      = 1024

    def __init__(self):
        self._client     = None
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
                self._callback(*Common.decomposeMessage(buffer))

    def setClient(self, client, callback = None):
        self.close()
        self._client = client
        self._client.setblocking(0)

    def getClient(self):
        return self._client

    def send(self, command, argument = ''):
        if self._client is None:
            return
        message = Common.composeMessage(command, argument)
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
            select.select([], [self._client], [])
            sent = self._client.send(data[total_send:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            total_send += sent

    def close(self):
        if self._client:
            try:
                self._client.shutdown(socket.SHUT_RDWR)
                self._client.close()
            except:
                pass
            self._client = None

    def fileno(self):
        if self._client:
            return self._client.fileno()
        return None

    def composeMessage(command, argument = ''):
        return command + ':' + json.dumps(argument)
        
    def decomposeMessage(message):
        message  = message.split(':')
        command  = message[0]
        argument = ':'.join(message[1:])
        try:
            argument = json.loads(argument)
        except:
            pass
        return (command, argument)

    def setWait(self, block):
        if block:
            self._timeoutSelect = None
        else:
            self._timeoutSelect = 0

    def run(self):
        while True:
            if self._client is None:
                return False

            inputready, outputready, exceptready = select.select([self._client], [], [], self._timeoutSelect)

            if self._client not in inputready:
                return True

            if self._size == 0:
                data_size = self.SIZE_LEN
            else:
                data_size = self._size - len(self._buffer)

            try:
                data = self._client.recv(data_size)
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
    def __init__(self, controller, module, screen_name):
        Common.__init__(self)

        if isinstance(controller, str):
            controller = controller.split(':')
            controller[1] = int(controller[1])
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(tuple(controller))

        self.setClient(client)

        self.send(module, screen_name)

class Server(Common):
    def __init__(self, client):
        Common.__init__(self)
        self.setClient(client)
        self.setCallback(self._receiveClientInformation)
        self.setWait(True)
        while not hasattr(self, '_screen_name'):
            self.run()

    def _receiveClientInformation(self, module, screen_name):
        self._module      = module
        self._screen_name = screen_name
        self.setCallback(None)
        self.setWait(False)

    def getClientInformation(self):
        return (self._module, self._screen_name)
