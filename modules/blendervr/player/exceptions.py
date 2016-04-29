# -*- coding: utf-8 -*-
# file: blendervr/player/exceptions.py

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

from ..exceptions import *

class CommonError(Exception):
    def __init__(self, reason):
        self._reason = reason

    def __str__(self):
        return self._reason
Common = CommonError


class MainError(CommonError):
    def __init__(self, reason):
        super(MainError, self).__init__(reason)
Main = MainError


class SynchronizerError(CommonError):
    def __init__(self, reason):
        super(SynchronizerError, self).__init__(reason)
Synchronizer= SynchronizerError


class ControllerError(CommonError):
    def __init__(self, reason):
        super(ControllerError, self).__init__(reason)
Controller = ControllerError


class UserError(CommonError):
    def __init__(self, reason):
        super(UserError, self).__init__(reason)
User = UserError


class VirtualEnvironmentError(CommonError):
    def __init__(self, reason):
        super(VirtualEnvironmentError, self).__init__(reason)
VirtualEnvironment = VirtualEnvironmentError


class ProcessorError(CommonError):
    def __init__(self, reason):
        super(ProcessorError, self).__init__(reason)
Processor = ProcessorError


class Processor_Invalid_DeviceError(CommonError):
    def __init__(self, reason):
        super(Processor_Invalid_DeviceError, self).__init__(reason)
Processor_Invalid_Device = Processor_Invalid_DeviceError


class Processor_Invalid_Device_MethodError(Processor_Invalid_DeviceError):
    def __init__(self, reason):
        super(Processor_Invalid_Device_Method, self).__init__(reason)
Processor_Invalid_Device_Method = Processor_Invalid_Device_MethodError
