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

from OpenGL.GL import *
from OpenGL.GLU import *
import copy
import math

class Reader:
    def __init__(self, file_name):
        vertices = ()
        textures = ()
        normals  = ()
        faces          = ()

        self._min = None
        self._max = None
        with open(file_name, 'r') as file:
            for line in file:
                line = line.strip().split(' ')
                command = line[0]
                arguments = line[1:]
                del(line)
                if command == 'v':
                    vertex = [float(arguments[0]), float(arguments[1]), float(arguments[2])]
                    vertices += (vertex, )
                    if self._min is None:
                        self._min = copy.copy(vertex)
                        self._max = copy.copy(vertex)
                    else:
                        for i in range(0, 3):
                            if self._min[i] > vertex[i]:
                                self._min[i] = vertex[i]
                            if self._max[i] < vertex[i]:
                                self._max[i] = vertex[i]
                elif command =='vt':
                    textures += ((float(arguments[0]), float(arguments[1])), )
                elif command == 'vn':
                    normals += ((float(arguments[0]), float(arguments[1]), float(arguments[2])), )
                elif command == 'f':
                    face = ()
                    for vertex in arguments:
                        vertex = vertex.split('/')
                        face = ()
                        for i in range(0, 3):
                            try:
                                face += (int(vertex[i]) - 1, )
                            except:
                                face += (None, )
                        faces += (face, )

        self._vertices = ()
        self._normals  = ()
        self._textures = ()
        self._indices = ()
        for face in faces:
            if face[0] is not None:
                element  = vertices[face[0]]
                self._vertices += (element[0], element[1], element[2], )
            if face[1] is not None:
                element  = textures[face[1]]
                self._textures += (element[0], element[1] )
            if face[2] is not None:
                element  = normals[face[2]]
                self._normals += (element[0], element[1], element[2], )
            self._indices += (len(self._indices), )

    def getMinMax(self):
        return (self._min, self._max)

    def draw(self, centered = True, normalized = True):
        if len(self._vertices):
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(3, GL_FLOAT, 0, self._vertices)
        if len(self._normals):
            glEnableClientState(GL_NORMAL_ARRAY)
            glNormalPointer(GL_FLOAT, 0, self._normals)
        if len(self._textures):
            glClientActiveTexture(GL_TEXTURE0)
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)
            glTexCoordPointer(2, GL_FLOAT, 0, self._textures)

        if centered or normalized:
            glPushMatrix()

        if centered:
            glTranslatef((self._max[0] + self._min[0]) / 2,
                         (self._max[1] + self._min[1]) / 2,
                         (self._max[2] + self._min[2]) / 2)

        if normalized:
            diagonal = (self._max[0] - self._min[0],
                        self._max[1] - self._min[1],
                        self._max[2] - self._min[2])
            scale = 2.0 / math.sqrt(diagonal[0] * diagonal[0] + diagonal[1] * diagonal[1] + diagonal[2] * diagonal[2])
            glScale(scale, scale, scale)
            

        glDrawElements(GL_TRIANGLES, len(self._indices), GL_UNSIGNED_INT, self._indices)

        if centered or normalized:
            glPopMatrix()

