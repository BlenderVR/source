# -*- coding: utf-8 -*-
# file: blendervr/player/network/connector.py

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

import struct
import socket
import select
from .. import exceptions
from .. import base
from ..buffer import Buffer
#import time

# Beware: we limit to 256 nodes
ID_SIZE = 1024
SIZE_FORMAT = '>i'
SIZE_SIZE = struct.calcsize(SIZE_FORMAT)

COMMAND_SIZE = 1
EVERYBODY_HERE = b'r'
BARRIER = b'b'


class Connector(base.Base):

    CMD_FINISHED = b'f'
    CMD_MSG = b'm'
    CMD_SYNCHRO = b's'

    def __init__(self, parent, config):
        base.Base.__init__(self, parent)

        port = config['port']
        try:
            connexion = port.split(':')
            self._address = connexion[0]
            self._port = int(connexion[1])
        except:
            self._address = None
            self._port = port
        self.BUFFER_SIZE = 4096

        self.isReady = lambda *args: False

    def selectSocket(self):
        inputready, outputready, exceptready = \
                                    select.select([self._socket], [], [])
        if self._socket in inputready:
            return True
        return False

    def receiveFrom(self, socket, size):
        try:
            data = b''
            while len(data) < size:
                chunk = socket.recv(size - len(data))
                if len(chunk) == 0:
                    raise Exception()
                data += chunk
            return data
        except:
            self._loosedConnexion(socket)

    def sendTo(self, socket, buffer):
        try:
            sended_size = 0
            buffer_size = len(buffer)
            while sended_size < buffer_size:
                chunk_size = socket.send(buffer[sended_size:])
                if chunk_size == 0:
                    raise Exception()
                sended_size += chunk_size
        except:
            self._loosedConnexion(socket)

class Master(Connector):

    def __init__(self, parent, config):
        Connector.__init__(self, parent, config)

        self.isMaster = lambda *args: True

        self._number_slaves = len(config['nodes']) - 1
        self._clients = {}

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(('', self._port))
        self._socket.listen(self._number_slaves)

        self._session = self.CMD_FINISHED

        if self._address is not None:
            self._multicast = socket.socket(socket.AF_INET,
                                    socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self._multicast.setsockopt(socket.IPPROTO_IP,
                                    socket.IP_MULTICAST_TTL, 2)

    def wait_for_everybody(self):
        if (self._number_slaves > 0) and self.selectSocket():
            client_socket, address = self._socket.accept()
            client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            try:
                screen_name = client_socket.recv(ID_SIZE).decode().rstrip()
            except socket.error:
                raise exceptions.Controller("Protocol error: client don't "
                                        "send correct connection message !")
            self.logger.info('Main Connection of a client [' +
                                        str(screen_name) + ']:', address)

            for index, client in self._clients.items():
                if client['name'] == screen_name:
                    raise exceptions.Controller("Protocol error : client "
                                                "already defined !")
            self._clients[client_socket] = {'name': screen_name,
                                            'socket': client_socket,
                                            'address': address}
        if len(self._clients) == self._number_slaves:
            for client in self._clients.keys():
                client.send(EVERYBODY_HERE)
            self.isReady = lambda *args: True

    def run(self):
        self._synchronizer.sendSynchronization()

    def endFrame(self):
        self.send(self.CMD_FINISHED, None)

    def barrier(self):
        if self.isReady():
            for client in self._clients.keys():
                message = self.receiveFrom(client, COMMAND_SIZE)
                if message != BARRIER:
                    self._loosedConnexion(client)
            for client in self._clients.keys():
                self.sendTo(client, BARRIER)

    def quit(self, reason):
        if hasattr(self, '_socket'):
            clients = list(self._clients.keys())
            for client in clients:
                try:
                    client.shutdown(socket.SHUT_RDWR)
                    client.close()
                    del(self._clients[client])
                except:
                    self.logger.warning(self.logger.EXCEPTION)
                    pass
                client = None
            del(clients)
            del(self._socket)
            self.blenderVR._quitByNetwork(reason)

    def send(self, session, buff):
        if not self.isReady():
            return
        if self._session != session:
            if self._session is not self.CMD_FINISHED:
                self._sendSize(0)
                self._session = None
            if session == self.CMD_MSG or\
                     session == self.CMD_SYNCHRO or \
                     session == self.CMD_FINISHED:
                self._session = session
                self._sending(self._session)
        if (session == self.CMD_MSG or session == self.CMD_SYNCHRO) and \
                                                        (len(buff) > 0):
            self._sendSize(len(buff._buffer))
            self._sending(buff._buffer)

    def sendToSlave(self, buff):
        self.send(self.CMD_MSG, buff)

    def _loosedConnexion(self, client):
        if client in self._clients:
            try:
                client.shutdown(socket.SHUT_RDWR)
                client.close()
            except:
                self.logger.warning(self.logger.EXCEPTION)
            message = 'Loosed connexion to "' + \
                                    self._clients[client]['name'] + '"'
            del(self._clients[client])
        else:
            message = 'Loosed connexion to a client'
        self.blenderVR.quit(message)

    def _sendSize(self, size):
        self._sending(struct.pack(SIZE_FORMAT, size))

    def _sending(self, data):
        clients = list(self._clients.keys())
        if len(clients) > 0:
            inputready, outputready, exceptready = \
                                            select.select([], clients, [])
            for client in clients:
                self.sendTo(client, data)


class Slave(Connector):

    def __init__(self, parent, config):
        Connector.__init__(self, parent, config)
        self.isMaster = lambda *args: False

        self._master = config['master']

        self._command = None

    def wait_for_everybody(self):
        if not hasattr(self, '_socket'):
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                self._socket.connect((self._master, self._port))
                self._socket.setsockopt(socket.IPPROTO_TCP,
                                socket.TCP_NODELAY, 1)  # improve speed ...
                ##TODO: specify encoding!
                self._socket.send(
                    self.blenderVR.getScreenName().ljust(ID_SIZE).encode())
            except socket.error as error:
                assert error    # avoid unused
                del(self._socket)
                return

            self.logger.info('Connected to master, waiting everybody '
                             'connected !')

        if self.selectSocket():
            ready = self._socket.recv(COMMAND_SIZE)
            if ready != EVERYBODY_HERE:
                raise exceptions.Controller("Protocol error: server don't "
                                            "send Everybody is here !")
            self.isReady = lambda *args: True

    def run(self):
        while True:
            command = self.receiveFrom(self._socket, COMMAND_SIZE)
            if command == self.CMD_MSG:
                command = self.blenderVR._messageFromMaster
            elif command == self.CMD_SYNCHRO:
                command = self._synchronizer.process
            else:     # self.CMD_FINISHED
                break
            while True:
                size = self._receiveSize()
                if size == 0:
                    break
                buff = Buffer()
                buff._buffer = self.receiveFrom(self._socket, size)
                command(buff)

    def endFrame(self):
        pass

    def barrier(self):
        if self.isReady():
            self.sendTo(self._socket, BARRIER)
            message = self.receiveFrom(self._socket, COMMAND_SIZE)
            if message != BARRIER:
                self._loosedConnexion(self._socket)

    def quit(self, reason):
        if hasattr(self, '_socket'):
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
                self._socket.close()
                del(self._socket)
            except:
                self.logger.warning(self.logger.EXCEPTION)
                pass
            self.blenderVR._quitByNetwork(reason)

    def _receiveSize(self):
        size = struct.unpack_from(SIZE_FORMAT,
                            self.receiveFrom(self._socket, SIZE_SIZE))
        return size[0]

    def _loosedConnexion(self, socket):
        self.blenderVR.quit('Lost connexion to master')
