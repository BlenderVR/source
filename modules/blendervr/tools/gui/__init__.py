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

try:

    import os
    import random
    if blenderVR_QT == 'PyQt4':
        from PyQt4 import QtGui
    else:
        from PySide import QtGui

    random.seed()

    def load(ui_file, parent_widget):
        fileName, fileExtension = os.path.splitext(ui_file)
        if fileExtension != '.ui':
            return None
        py_file = fileName + '.py'
        if not os.path.isfile(py_file) or os.path.getmtime(py_file) < os.path.getmtime(ui_file):
            if blenderVR_QT == 'PyQt4':
                command = 'pyuic4 -w'
            else:
                command = 'pyside-uic'
            os.system(command + ' -o ' + py_file + ' ' + ui_file)

        module_path = os.path.dirname(py_file)
        if not os.path.isdir(module_path):
            return None
    
        module_name = os.path.splitext(os.path.basename(py_file))[0]
        try:
            import imp
            (file, file_name, data) = imp.find_module(module_name, [module_path])
        except:
            return None

        try:
            module = imp.load_module('ui_' + str(random.randrange(268431360)), file, file_name, data)
        except:
            return None

        import inspect
        for name in dir(module):
            element = getattr(module, name)
            if inspect.isclass(element):
                result = element()
                result.setupUi(parent_widget)
                return result
        return None

    def insertWidgetInsideAnother(parent, child):
        child.setParent(parent)
        grid = QtGui.QGridLayout(parent)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.addWidget(child, 0, 0, 1, 1)
        return grid

except:
    pass
