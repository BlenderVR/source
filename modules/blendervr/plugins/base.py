# -*- coding: utf-8 -*-
# file: blendervr/plugins/base.py

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

from .. import *


class Common:
    def __init__(self):
        pass

    def getName(self):
        return self._name


if is_virtual_environment():
    from ..player import base

    class PluginBase(Common, base.Base):
        def __init__(self, parent):
            Common.__init__(self)
            base.Base.__init__(self, parent)

            self._main = None

        def setupMain(self, master_only):
            """setup the plugin if it runs in master only"""
            if not master_only or self.BlenderVR.isMaster():
                self.run = self._main.run
                self._main.start()

        def setConfiguration(self, configuration):
            pass

        def isValid(self):
            return True

        def quit(self):
            pass

        def start(self):
            pass

        def run(self):
            pass

        @property
        def virtual_environment(self):
            return self._main
    Base = PluginBase

elif is_console():
    from ..console import base

    class PluginBase(Common, base.Base):
        def __init__(self, parent):
            Common.__init__(self)
            base.Base.__init__(self, parent)

        def start(self):
            pass

        def quit(self):
            pass

        def getXMLParserClass(self):
            return None
    Base = PluginBase

