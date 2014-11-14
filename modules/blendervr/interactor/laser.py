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

import blendervr

if blendervr.is_virtual_environment():

    import bge
    import mathutils
    import bgl
    from ..player.base import Base
    from ..player.buffer import Buffer

    class Laser(Base):

        def __init__(self, parent, object, sensor):
            Base.__init__(self, parent)

            self._scene  = bge.logic.getCurrentScene()

            self._allowedObjects = []

            self._laser_object = object
            self._sensor       = sensor
            self._ray          = {'origin' : mathutils.Vector(),
                                  'destin' : mathutils.Vector(),
                                  'color'  : [1.0, 1.0, 1.0] }

            self.attachLaserToCamera()

            self._scene.pre_draw.append(self.display_laser)
            self.blenderVR.addObjectToSynchronize(self, 'laser beam')

        def allowDisallowObjects(self, allow, objects = None):
            if objects is None:
                objects = self._scene.objects
            if type(objects).__name__ == 'list' or type(objects).__name__ == 'CListValue':
                for object in objects:
                    self.allowDisallowObjects(allow, object)
                return
            if allow:
                if not objects in self._allowedObjects:
                    self._allowedObjects.append(objects)
            else:
                if objects in self._allowedObjects:
                    self._allowedObjects.remove(objects)

        def getObject(self):
            return self._laser_object

        def attachLaserToCamera(self):
            camera = self._scene.active_camera
            self._laser_object.worldPosition    = camera.worldPosition
            self._laser_object.worldOrientation = camera.worldOrientation
            self._laser_object.setParent(camera)


        def getSynchronizerBuffer(self):
            ray_vec = mathutils.Vector(self._sensor.rayDirection)
            ray_vec.magnitude = self._sensor.range

            self._ray['origin'] = mathutils.Vector(self._laser_object.worldPosition)

            if self._sensor.positive:
                hit_vec = mathutils.Vector(self._sensor.hitPosition)
                ray_vec = hit_vec - self._ray['origin']

            self._ray['destin'] = self._ray['origin'] + ray_vec

            buffer = Buffer()
            buffer.vector_3(self._ray['origin'])
            buffer.vector_3(self._ray['destin'])

            return buffer

        def processSynchronizerBuffer(self, buffer):
            while not buffer.isEmpty():
                self._ray['origin'] = buffer.vector_3()
                self._ray['destin'] = buffer.vector_3()


        def display_laser(self):
            bgl.glColor3f(self._ray['color'][0], self._ray['color'][1], self._ray['color'][2])
            bgl.glLineWidth(1.0)

            bgl.glBegin(bgl.GL_LINES)
            bgl.glVertex3f(self._ray['origin'].x, self._ray['origin'].y, self._ray['origin'].z)
            bgl.glVertex3f(self._ray['destin'].x, self._ray['destin'].y, self._ray['destin'].z)
            bgl.glEnd()


        def grab(self):
            if (not hasattr(self, '_grabbed_object')) and (self._sensor.hitObject is not None) and (self._sensor.hitObject in self._allowedObjects):
                self._grabbed_object = self._sensor.hitObject
                self._grabbed_object.setParent(self._laser_object)

        def release(self):
            if hasattr(self, '_grabbed_object'):
                self._grabbed_object.removeParent()
                del(self._grabbed_object)

        def toggle(self):
            if hasattr(self, '_grabbed_object'):
                self.release()
            else:
                self.grab()

        def getHitObject(self, grabbed = False):
            if hasattr(self, '_grabbed_object'):
                return self._grabbed_object
            if (not grabbed) and (self._sensor.hitObject is not None):
                return self._sensor.hitObject
            return None
        
elif blendervr.is_creating_loader():
    import bpy

    from ..loader.base import Base

    class Laser(Base):
        def __init__(self, parent):
            Base.__init__(self, parent)

        def process(self, controller):
            print('Laser creation !')
