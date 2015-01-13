# -*- coding: utf-8 -*-
# file: blendervr/plugins/vrpn/virtual_environment/tracker.py

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

import vrpn
import mathutils
from ....player import device, exceptions


class _Sensor(device.Sender):
    def __init__(self, parent, configuration):
        super(_Sensor, self).__init__(parent, configuration)
        self._id = configuration['id']
        for when in ['pre', 'post']:
            result = mathutils.Matrix()
            for operation in configuration['transformation'][when]:
                if 'rotation' in operation:
                    operands = operation['rotation']
                    operation = mathutils.Matrix.Rotation(operands['angle'],
                                                4, tuple(operands['vector']))
                elif 'translation' in operation:
                    operands = operation['translation']
                    operation = mathutils.Matrix.Translation(
                                            tuple(operands['vector']))
                else:
                    continue
                result = operation * result
            setattr(self, '_' + when + '_transformation', result)

    def getID(self):
        return self._id

    def run(self, info):
        matrix = info['matrix']
        matrix *= self._pre_transformation
        if self.getTracker()._scale is not None:
            for i in range(0, 3):
                matrix[3][i] *= self.getTracker()._scale
        info['matrix'] = self._post_transformation * matrix
        self.process(info)

    def __str__(self):
        return self.getTracker().__str__() + '[' + str(self._id) + ']'

    def getTracker(self):
        return self.getParent()


class Tracker(device.Receiver):
    def __init__(self, parent, configuration):
        super(Tracker, self).__init__(parent, configuration)
        self._scale = configuration['scale']

        if 'sensors' not in configuration:
            raise exceptions.Processor_Invalid_Device('VRPN tracker must '
                                                'have at least one sensor')
        self._sensors = {}
        for element in configuration['sensors']:
            try:
                sensor = _Sensor(self, element)
            except exceptions.Processor_Invalid_Device_Method as method:
                if self.getParent()._display_processors:
                    self.logger.warning(method)
            except exceptions.Processor_Invalid_Device as other:
                self.logger.warning(other)
            else:
                self._sensors[sensor.getID()] = sensor

    def start(self):
        self._connexion = vrpn.receiver.Tracker(self._name + "@" + self._host)
        self._connexion.register_change_handler(None,
                                self._position, "position")
        self._connexion.register_change_handler(None,
                                self._workspace_handler, "workspace")
        self._connexion.register_change_handler(None,
                                self._unit2sensor_handler, "unit2sensor")
        self._connexion.register_change_handler(None,
                                self._tracker2room_handler, "tracker2room")
        #self._connexion.request_t2r_xform()
        #self._connexion.request_u2s_xform()
        #self._connexion.request_workspace()

    def _getMatrix(self, info, position_name='position',
                                        quaternion_name='quaternion'):
        orientation = mathutils.Matrix(
                (vrpn.quaternion.to_col_matrix(info[quaternion_name])))
        orientation.resize_4x4()
        position = mathutils.Matrix.Translation(
                (info[position_name][0],
                 info[position_name][1],
                 info[position_name][2]))
        return position * orientation

    def _position(self, data, info):
        sensor = info['sensor']
        if sensor in self._sensors:
            new_information = {'matrix': self._getMatrix(info),
                               'time': info['time']}
            self._sensors[sensor].run(new_information)

    def _workspace_handler(self, data, info):
        self._workspace['min'] = info['minimum corner box']
        self._workspace['max'] = info['maximum corner box']

    def _tracker2room_handler(self, data, info):
        self._transformation = self._getMatrix(info, 'position offset',
                                                    'quaternion offset')

    def _unit2sensor_handler(self, data, info):
        sensor = info['sensor']
        if sensor in self._sensors:
            self._sensors[sensor]._transformation = \
                self._getMatrix(info, 'position offset', 'quaternion offset')

    def checkMethod(self, display_processors):
        invalid = []
        for index, sensor in self._sensors.items():
            if not sensor.checkMethod(display_processors):
                invalid.append(index)
        for index in invalid:
            del(self._sensors[index])
        return len(self._sensors) > 0
