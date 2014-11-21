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
import mathutils

class Buffer:

    def __init__(self):
        self._buffer = b''

    def __len__(self):
        return len(self._buffer)

    def isEmpty(self):
        return (len(self) == 0)

    def command(self, data = None):
        return self._simpleData('c', data)

    def boolean(self, data = None):
        return self._simpleData('?', data)

    def unsigned_char(self, data = None):
        return self._simpleData('B', data)

    def size(self, data = None):
        return self.integer(data)

    def itemID(self, data = None):
        return self._simpleData('>Q', data)

    def integer(self, data = None):
        return self._simpleData('>i', data)

    def float(self, data = None):
        return self._simpleData('>f', data)

    def subBuffer(self, data = None):
        if data is None:
            data = Buffer()
            data._buffer = self._subBytes(None)
            return data
        self._subBytes(data._buffer)

    def string(self, data = None):
        if data is None:
            return self._subBytes(None).decode('UTF-8')
        self._subBytes(bytes(data, 'UTF-8'))

    def vector_3(self, data = None):
        if data is None:
            data = self._extract(">3f")
            return mathutils.Vector(data)
        self._buffer += struct.pack(">3f", data[0], data[1], data[2])

    def vector_4(self, data = None):
        if data is None:
            data = self._extract(">4f")
            return mathutils.Vector(data)
        self._buffer += struct.pack(">4f", data[0], data[1], data[2], data[3])

    def matrix_3x3(self, data = None):
        if data is None:
            data = self._extract(">9f")
            return mathutils.Matrix(((data[0], data[1], data[2]),
                                     (data[3], data[4], data[5]),
                                     (data[6], data[7], data[8])))
        self._buffer += struct.pack(">9f", data[0][0], data[0][1], data[0][2],
                                           data[1][0], data[1][1], data[1][2],
                                           data[2][0], data[2][1], data[2][2])

    def matrix_4x4(self, data = None):
        if data is None:
            data = self._extract(">16f")
            return mathutils.Matrix(((data[ 0], data[ 1], data[ 2], data[ 3]),
                                     (data[ 4], data[ 5], data[ 6], data[ 7]),
                                     (data[ 8], data[ 9], data[10], data[11]),
                                     (data[12], data[13], data[14], data[15])))

        self._buffer += struct.pack(">16f", data[0][0], data[0][1], data[0][2], data[0][3],
                                            data[1][0], data[1][1], data[1][2], data[1][3],
                                            data[2][0], data[2][1], data[2][2], data[2][3],
                                            data[3][0], data[3][1], data[3][2], data[3][3])

    def addPrefix(self, prefix):
        if isinstance(prefix, Buffer):
            self._buffer = prefix._buffer + self._buffer
            return self

    def _subBytes(self, data = None):
        if data is None:
            size = self.size()
            buffer = self._buffer[:size]
            self._buffer = self._buffer[size:]
            return buffer
        self.size(len(data))
        self._buffer += data

    def _extract(self, format):
        values = struct.unpack_from(format, self._buffer)
        self._buffer = self._buffer[struct.calcsize(format):]
        return values

    def _simpleData(self, format, data):
        if data is None:
            data = self._extract(format)
            return data[0]
        self._buffer += struct.pack(format, data)

    def __iadd__(self, other):
        if isinstance(other, Buffer):
            self._buffer += other._buffer
            return self

    def __add__(self, other):
        if isinstance(other, Buffer):
            result = Buffer()
            result._buffer = self._buffer + other._buffer
            return result

def data_size(data_type):
    if data_type == 'command':
        return struct.calcsize('c')
    if data_type == 'boolean':
        return struct.calcsize('?')
    if data_type == 'unsigned_char':
        return struct.calcsize('B')
    if data_type == 'size':
        return data_size('integer')
    if data_type == 'itemID':
        return struct.calcsize('>Q')
    if data_type == 'integer':
        return struct.calcsize('>i')
    if data_type == 'float':
        return struct.calcsize('>f')
    if data_type == 'vector3':
        return struct.calcsize('>3f')
    if data_type == 'matrix_3x3':
        return struct.calcsize('>9f')
    if data_type == 'matrix_4x4':
        return struct.calcsize('>16f')

