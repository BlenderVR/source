# -*- coding: utf-8 -*-
# file: blendervr/tools/connector.py

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
"""\
Manage TCP connections between BlenderVR components to transmit command + data messages.

As TCP is stream based, messages are split into a fixed header containing message size
followed by message itself. The fixed header is SIZE_LEN bytes length and contain 
string representation of the message size. The message is a sequence of bytes contructed
using protocol module functions (for command + data content).

Note: blendervr.player.network.connector define their own communication mechanism.
"""

import sys
import socket
import select

from blendervr.tools import protocol

import logging
logger = logging.getLogger(__name__)

# Set to true to print packets to (real) stdout (sys.__stdout__). Help debugging.
SOCKET_DEBUG = True


class ConnectorCommon:
    """Common connector processing TCP communications for command+data messages.

    Subclasses are specialized for server or client side of the communications.

    User or subclass must call set_tcp_pair() method to associate a socket to
    the connector, and setCallback() to associate a processing function for
    incoming messages.

    :const SIZE_LEN: length of chunk to transmit data length at beginning of TCP packets.
    :const BUFFER_LEN: max length of transmitted chunks when writting TCP data packets.
    :ivar _tcpsocket: Socket for communications.
    :type _tcpsocket: Socket
    :ivar _callback: function to call on message reception.
    :type _callback: f(message, data)
    :ivar _received_buffers: list of received buffers containing messages.
    :type _received_buffers: [ b'']
    :ivar _size: remaining data size to read from _tcpsocket into _read_buffer.
    :type _size: int
    :ivar _read_buffer: currently read bytes of a streamed message.
    :type _read_buffer: b''
    """
    SIZE_LEN = 10
    BUFFER_LEN = 1024

    def __init__(self):
        self._tcpsocket = None
        self._callback = None
        self._received_buffers = []
        self._size = 0
        self._read_buffer = b''

        self.setWait(True)

    def __str__(self):
        if self._tcpsocket is not None:
            return str("<{} id {} socket {}>".format(self.__class__.__name__, id(self), self._tcpsocket))
        else:
            return str("<{} id {}>".format(self.__class__.__name__, id(self)))

    def _process_read_buffer(self):
        """Get read bytes buffer and store it decoded into buffers list.
        """
        # If some pending data in buffer, decode and queue it.
        if len(self._read_buffer) > 0:
            # Note: default encoding for decode is utf8.
            self._received_buffers.append(self._read_buffer.decode())
        # Reset prepare next read.
        self._size = 0
        self._read_buffer = b''

    def __del__(self):
        self.close()

    def setCallback(self, callback):
        """Specify function to call when a message is received.

        Pending buffers (messages) are processed with this callback.
        """
        if SOCKET_DEBUG:
            if self._tcpsocket:
                print("!! Socket {} with callback {}".format(self._tcpsocket.fileno(), callback), file=sys.__stdout__)
        self._callback = callback
        self._process_received_buffers()

    def _process_received_buffers(self):
        """Process all< pending buffers as messages via callback function.
        """
        if self._callback:
            while len(self._received_buffers) > 0:
                # Note: messages are processed in their coming order.
                buff = self._received_buffers.pop(0)
                self._callback(*protocol.decomposeMessage(buff))

    def set_tcp_pair(self, client):
        # Note: removed unused callback parameter.
        self.close()
        if SOCKET_DEBUG:
            print("!! Associate socket  {} for {} ({})".format(client.fileno(), self, client), file=sys.__stdout__)
        self._tcpsocket = client
        self._tcpsocket.setblocking(0)

    def get_client(self):
        return self._tcpsocket

    def send_command(self, command, argument=''):
        """Send a command and its arguments to a server.
        """
        if self._tcpsocket is None:
            return
        # Message sent prefixed by its size represented as text in a
        # SIZE_LEN chunk.
        # Note: by default string encode() and bytes decode() use
        # utf-8 encoding in Python3.
        message = protocol.composeMessage(command, argument)
        size = str(len(message)).zfill(self.SIZE_LEN)
        self._send_chunk(size.encode())
        while len(message) > 0:
            buff = message[:self.BUFFER_LEN]
            message = message[self.BUFFER_LEN:]
            self._send_chunk(buff.encode())

    def send(self, command, argument=''):
        """Send a command and its arguments to a server.

        Kept for compatibility - prefer use send_command() to distinguish between all 
        "send" usages.
        """
        # TODO: add somt tracing with frame to identify what lines still call this method.
        raise RuntimeError("SOMEONE STILL USE OLD send() FOR MESSAGES")
        if False:
            import inspect
            frame = inspect.currentframe()
            try:
                print("send() called from ", frame, file=sys.__stdout__)
                # do something with the frame
            finally:
                del frame
        return self.send_command(command, argument)

    # Be carefull: we use non blocking socket. So, we must wait for the 
    # TCP stream buffer to be empty before sending elements ...
    def _send_chunk(self, data):
        total_send = 0
        while total_send < len(data):
            if SOCKET_DEBUG:
                print(">> send Socket {} >> {!r}".format(self._tcpsocket.fileno(), data), file=sys.__stdout__)
            # Wait for socket to be ready for writing.
            try:
                select.select([], [self._tcpsocket], [])   # blocking select
            except Exception as e:
                if SOCKET_DEBUG:
                    print("!! {} : {}".format(self, e), file=sys.__stdout__)
                raise
            sent = self._tcpsocket.send(data[total_send:])
            if sent == 0:
                logger.error("Socket connection broken.")
                raise RuntimeError("socket connection broken")
            total_send += sent

    def close(self):
        if self._tcpsocket:
            if SOCKET_DEBUG:
                print("!! Socket close {}".format(self), file=sys.__stdout__)
            try:
                self._tcpsocket.shutdown(socket.SHUT_RDWR)
                self._tcpsocket.close()
            except:
                pass
            self._tcpsocket = None

    def fileno(self):
        if self._tcpsocket:
            return self._tcpsocket.fileno()
        return None

    def setWait(self, block):
        if block:
            self._timeoutSelect = None
        else:
            self._timeoutSelect = 0

    def run(self):
        """Read from connector TCP socket if available.

        If a complete packet has been received, the method decompose
        it as a message (following protocol rules) and call its callback with
        that message parts (via flushBuffers()).

        The method return when there is nothing to read (or no socket).

        :return: that is the question, what is the meaning of return value?
        :rtype: bool
        """
        while True:
            if self._tcpsocket is None:
                return False

            inputready, outputready, exceptready = select.select(
                            [self._tcpsocket], [], [], self._timeoutSelect)

            if self._tcpsocket not in inputready:
                return True

            if self._size == 0:
                data_size = self.SIZE_LEN
            else:
                data_size = self._size - len(self._read_buffer)

            try:
                data = self._tcpsocket.recv(data_size)
                if SOCKET_DEBUG:
                    print("<< recv Socket {} << {!r}".format(self._tcpsocket.fileno(), data), file=sys.__stdout__)
            except:
                data = False
            if not data:
                self.close()
                return False

            if self._size == 0:
                try:
                    self._size = int(data)
                except:
                    logger.error("Invalid data_size prefix in packet: %r", data)
                    # TODO: unsynchronization. Should close the socket on our
                    # server side, and client should re-open it.
                    raise
            else:
                # Accumulate read data into buffer until reach target size.
                self._read_buffer += data
                if len(self._read_buffer) == self._size:
                    # Queue received data, and prepare next read, then
                    # process queued data as messages.
                    self._process_read_buffer()
                    self._process_received_buffers()
Common = ConnectorCommon

class TcpClientMgr(ConnectorCommon):
    def __init__(self, controller, module, screen_name):
        """\
        Initialize a client connector.

        If the controller is a string, it is considered to be "host:port".

        :param controller: host and port of TCP server controlling the client.
        :type controller: string   or   (string, int)
        :param module: identifier of module to transmit.
        :type module: string
        :param screen_name: identifier of the screen to transmit.
        :type screen_name: string
        """
        logger.debug("Creating client connector to %s for %s %s", controller, module, screen_name)
        ConnectorCommon.__init__(self)

        # Accept "host:port" controller.
        if isinstance(controller, str):
            controller = controller.split(':')
            controller[1] = int(controller[1])
        else:
            assert isinstance(controller[0], str)
            assert isinstance(controller[1], int)
        assert len(controller) == 2

        # Establish our TCP connection to the server.
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(tuple(controller))

        self.set_tcp_pair(client)

        # Inform our TCP pair about the module and screen name connected.
        self.send_command(module, screen_name)
# Keep compatibility with name.
Client = TcpClientMgr

class TcpServerConMgr(ConnectorCommon):
    def __init__(self, client):
        """\
        Initialize a client connector.

        This is a TCP socket manager created when a TCP client has been connected to a 
        TCP master socket.
        
        :param client: communication path to the client
        :type client: Socket
        """
        logger.debug("Creating server connector for socket %s", client)
        ConnectorCommon.__init__(self)
        self.set_tcp_pair(client)
        # Prepare reception of client identity informations.
        self.setCallback(self._receiveClientInformation)
        self.setWait(True)
        # Loop read for our TCP pair to send its identity (module and screen name).
        while not hasattr(self, '_screen_name'):
            self.run()

    def _receiveClientInformation(self, module, screen_name):
        """Initial callback to receive client identity informations.
        """
        self._module = module
        self._screen_name = screen_name
        # No longer process with this callback.
        self.setCallback(None)
        self.setWait(False)

    def getClientInformation(self):
        """Return identity of client connected to this server.
        """
        return (self._module, self._screen_name)
# Keep compatibility with name.
Server = TcpServerConMgr