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
from ...tools import protocol
from ...tools import controller
from . import base

class Client(controller.Common):
    def __init__(self, _socket):
        controller.Common.__init__(self)
        self.setSocket(_socket)
        result = self.receive()
        if result:
            self._module     = result[0]
            self._complement = result[1]

    def getClientInformation(self):
        return (self._module, self._complement)

class Listener(base.Base):
    def __init__(self, parent):
        base.Base.__init__(self, parent)
        self._clients = {}

        self._socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._port    = 31415
        while True:
            try:
                self._socket.bind(('', self._port))
                break
            except socket.error:
                self._port += 1

        self._socket.listen(100)
        self._client_processor = self.getMainRunningModule()._connect_client
        self.addCallback(self._socket, self._connect_client)

    def select(self):
        inputready, outputready, exceptready = select.select(self._clients.keys(), [], [])
        for sock in inputready:
            if sock in self._clients:
                try:
                    self._clients[sock]()
                except controller.closedSocket:
                    self.delCallback(sock)
                except:
                    self.log_traceback()

    def _connect_client(self):
        conn, addr = self._socket.accept()
        client = Client(conn)
        self._client_processor(client)
        return True
        
    def getPort(self):
        return self._port

    def _getSocketDescriptor(client):
        if isinstance(client, controller.Common):
            return client.getSocket()
        elif isinstance(client, socket.socket):
            return client
        return False

    def addCallback(self, client, callback):
        socket = Listener._getSocketDescriptor(client)
        if socket:
            self._clients[socket] = callback
            return True
        return False

    def delCallback(self, client):
        socket = Listener._getSocketDescriptor(client)
        if socket and socket in self._clients:
            del(self._clients[socket])
            return True
        return False
        
                
        
