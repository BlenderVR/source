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

import readline
from . import base
from ...tools.protocol.root import Root
    
class Completer(base.Base):

    def __init__(self, parent):
        base.Base.__init__(self, parent)

        readline.set_completer(self.complete)
        readline.parse_and_bind('tab: complete')


        self._options = {}
        self._addLevel(Root)
        self.logger.debug(self._options)

    def _addLevel(self, _class):
        forbidden = ['ask', 'getConnection', 'send', 'children']
        self._options[_class.__name__] = []
        for method in dir(_class):
            if not method.startswith('_') and method not in forbidden:
                self._options[_class.__name__].append(method)
        if hasattr(_class, 'children'):
            for children in _class.children():
                self._options[_class.__name__].append(children.__name__)
                self._addLevel(children)        
        
    def getOptions(self, text):
        return sorted(['start', 'stop', 'list', 'print'])
                
    def complete(self, text, state):
        try:
            response = None
            if state == 0:
                options = self.getOptions(text)
                # This is the first time for this text, so build a match list.
                if text:
                    self.matches = [s 
                                    for s in options
                                    if s and s.startswith(text)]
                else:
                    self.matches = options[:]
        
            # Return the state'th item from the match list,
            # if we have that many.
            try:
                response = self.matches[state]
            except IndexError:
                response = None
            return response
        except:
            self.logger.log_traceback(True)

