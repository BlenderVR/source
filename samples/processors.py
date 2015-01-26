# -*- coding: utf-8 -*-
# file: samples/processors.py

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
    import math
    from blendervr.player import device

    class Common(blendervr.processor.getProcessor()):
        def __init__(self, parent, head_navigator=None, laser=False,
                                                    use_viewpoint=False):
            super(Common, self).__init__(parent)

            if laser:
                controller = bge.logic.getCurrentController()
                from blendervr.interactor.laser import Laser
                self._laser = Laser(self, controller.owner,
                                                controller.sensors[laser])

            if self.blenderVR.isMaster() and head_navigator is not None:
                if type(head_navigator) is not dict:
                    head_navigator = {}
                if 'method' not in head_navigator:
                    head_navigator['method'] = None
                if 'one_per_user' not in head_navigator:
                    head_navigator['one_per_user'] = True

                from blendervr.interactor.head_controlled_navigation import (
                                                                        HCNav)
                self._navigator = HCNav(self, method=head_navigator['method'],
                                one_per_user=head_navigator['one_per_user'])
                self._navigator.setDefaultUser(
                                        self.blenderVR.getUserByName('user A'))
                self.registerInteractor(self._navigator)

            if use_viewpoint:
                from blendervr.interactor.viewpoint import ViewPoint
                self._viewpoint = ViewPoint(self)
                self._viewpoint.viewpointScale = 0.2
                self.registerInteractor(self._viewpoint)

        def user_position(self, info):
            super(Common, self).user_position(info)
            if hasattr(self, '_navigator'):
                for user in info['users']:
                    self._navigator.setHeadLocation(user, info)

        def tracker_1(self, info):
            if hasattr(self, '_laser'):
                obj = self._laser.getObject()
                obj.localPosition = info['matrix'].to_translation()
                obj.localOrientation = info['matrix'].to_3x3() \
                    * mathutils.Matrix.Rotation(math.radians(-90.0), 3, 'X')

        def texts(self, info):
            self.logger.debug(info['message'])
            if info['message'] == 'COMPUTER QUIT':
                self.blenderVR.quit("because user asked !")
            if hasattr(self, '_navigator'):
                cmd = None
                if info['message'] == 'COMPUTER CALIBRATION':
                    cmd = self._navigator.CALIBRATE
                elif info['message'] == 'COMPUTER NAVIGATION':
                    cmd = self._navigator.TOGGLE
                elif info['message'] == 'COMPUTER HOME':
                    self.reset(info['users'])

                if cmd is not None:
                    for user in info['users']:
                        self._navigator.update(cmd, user)
                    self.sendToConsole('navigation_state',
                                self._navigator.getNavigationState())

        def reset(self, users = None):
            if not hasattr(self, '_navigator'):
                return
            if users is None:
                users = list(self.blenderVR.getAllUsers().values())
            for user in users:
                self._navigator.update(self._navigator.RESET, user)
                user.resetVehiclePosition()

        def keyboardAndMouse(self, info):
            try:
                if info['key'] == ord('q'):
                    self.blenderVR.quit("pressed 'q' key")
                if (info['key'] == ord('v')
                        and info['state'] == device.STATE_PRESS
                        and hasattr(self, '_viewpoint')):
                    self._viewpoint.activation(
                                    not self._viewpoint.isActivated())
                    return
            except (KeyError, SystemExit):
                pass
            except:
                self.logger.error(self.logger.EXCEPTION)
            super(Common, self).keyboardAndMouse(info)

elif blendervr.is_creating_loader():
    import bpy
    assert bpy    # avoid imported but unused

    class Processor(blendervr.processor.getProcessor()):

        def __init__(self, creator, laser=False):
            super(Processor, self).__init__(creator)
            if laser:
                from blendervr.interactor.laser import Laser
                self._laser = Laser(self)

        def process(self, controller):
            if hasattr(self, '_laser'):
                self._laser.process(controller)

elif blendervr.is_console():

    from blendervr.tools.gui.qt import QtGui

    class Common(blendervr.processor.getProcessor()):

        def __init__(self, parent, ui_path=None, head_navigator=None):
            super(Common, self).__init__(parent)

            # The common processor should be loaded at first !
            self._window = QtGui.QDialog()
            if ui_path:
                self._ui = blendervr.tools.gui.load(ui_path, self._window)
                try:
                    self._ui.navigation.clicked.connect(self.cb_navigation)
                    self._ui.calibration.clicked.connect(self.cb_calibration)
                    self._ui.home.clicked.connect(self.cb_home)
                except:
                    pass

            if head_navigator is not None:
                from blendervr.interactor.head_controlled_navigation import (
                                                                        HCNav)
                self._navigator = HCNav(self)
                self.registerInteractor(self._navigator)

        def show(self):
            self._window.show()

        def hide(self):
            self._window.hide()

        def quit(self):
            self._window.close()
            super(Common, self).quit()
