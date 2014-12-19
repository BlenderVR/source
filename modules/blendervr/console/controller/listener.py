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
import sys
from ...tools import protocol
from ...tools import controller
from . import base

class Client(controller.Common):
    def __init__(self, sock):
        controller.Common.__init__(self)
        self.setSocket(sock)
        result = self.receive()
        if result:
            self._module     = result[0]
            self._complement = result[1]
        self._peername = self._socket.getpeername()

    def __str__(self):
        return str(self._peername[0])

    def getClientInformation(self):
        return (self._module, self._complement)

class Listener(base.Base):
    def __init__(self, parent):
        base.Base.__init__(self, parent)
        self._sockets = []
        self._peers = {}

        self._socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._port    = 31415
        while True:
            try:
                self._socket.bind(('', self._port))
                break
            except socket.error:
                self._port += 1

        self._socket.listen(100)
        self._sockets.append(self._socket)

    def select(self):
        inputready, outputready, exceptready = select.select(self._sockets, [], [])
        for sock in inputready:
            if sock == self._socket:
                self._connect_peer()
            if sock in self._peers:
                try:
                    self._peers[sock].cb_data()
                except controller.closedSocket:
                    self._disconnect_peer(sock)
                except SystemExit:
                    for sock in self._sockets:
                        self._disconnect_peer(sock)
                        sock.shutdown(socket.SHUT_RDWR)
                        sock.close()
                    sys.exit()
                except:
                    self.logger.log_traceback(False)

    def _connect_peer(self):
        conn, addr = self._socket.accept()
        client = Client(conn)
        peer = self.getMainRunningModule()._create_client(client)
        self._sockets.append(conn)
        self._peers[conn] = peer
        peer._listenet_required_client = client
        peer.cb_connect()

    def _disconnect_peer(self, sock):
        if sock in self._sockets:
            self._sockets.remove(sock)
        if sock in self._peers:
            peer = self._peers[sock]
            del(self._peers[sock])
            peer.cb_disconnect()
            self.getMainRunningModule()._delete_client(peer)

    def getPort(self):
        return self._port

        
                
        
