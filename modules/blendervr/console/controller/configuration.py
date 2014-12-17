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

from . import base

class Configuration(base.Base):
    def __init__(self, parent):
        base.Base.__init__(self, parent)
        self.load()

    def load(self):
        try:
            configuration_file = self.profile.getValue(['config', 'file'])
            if configuration_file is None:
                return
            configuration_paths = copy.copy(self.profile.getValue(['config', 'path']))

            configuration_path = os.path.dirname(configuration_file)
            # Don't remove the path from the configuration file, otherwise, other paths will be prioritaries !
            # configuration_file = os.path.basename(configuration_file)

            if configuration_paths is None:
                configuration_paths = [configuration_path]
            elif configuration_path not in configuration_paths:
                configuration_paths.append(configuration_path)

            previous_common_processors = self._common_processors

            from .. import xml
            config              = xml.Configure(self, configuration_paths, configuration_file)
            self._configuration = config.getConfiguration()

            starter            = self._configuration['starter']
            self._net_console  = starter['hostname'] + ':' + str(self._port)
            self._anchor       = starter['anchor']
            self._screenSets   = starter['configs']
            self._blender_exe  = starter['blender']
            possibleScreenSets = list(self._screenSets.keys())

            self._common_processors = self._configuration['processors']

            if self._possibleScreenSets != possibleScreenSets:
                self._possibleScreenSets = possibleScreenSets
                self.display_screen_sets(self._possibleScreenSets)
            self.set_screen_set()

        except SystemExit:
            raise
        except exceptions.Main as error:
            self.logger.error(str(error))
        except:
            self.logger.log_traceback(False)
