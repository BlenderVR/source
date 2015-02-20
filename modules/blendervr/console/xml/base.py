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

import os
import sys
import xml.sax.handler
import xml.sax.xmlreader
from . import Configure
import math
from ..base import Base

class XML(xml.sax.handler.ContentHandler, Base):
    def __init__(self, parent, name, attrs):
        xml.sax.handler.ContentHandler.__init__(self)
        Base.__init__(self, parent)

        self._xml_reader             = self._parent._xml_reader
        self._locator          = self._parent._locator
        self._parser           = self._parent._parser
        self._xml_section_name = name
        self._attribute_list   = []
        self._class_list       = []
        self._attributs_inheritance = {}

    def startElement(self, name, attrs):
        child = self._getChildren(name, attrs)
        if child is not None:
            self._parser.setContentHandler(child)

    def endElement(self, name):
        if name == self._xml_section_name:
            self._parser.setContentHandler(self._parent)

    def getParser(self):
        return self._parser

    def getMain(self):
        return self._xml_reader

    def getXML_LineNumber(self):
        return self._locator.getLineNumber()

    def getXML_FileName(self):
        return self._locator.getSystemId()

    def getXML_Position(self):
        return 'line ' + str(self.getXML_LineNumber()) + ' of ' + self.getXML_FileName()

    def raise_error(self, msg):
        from .. import exceptions
        raise exceptions.Main(msg +' (' + self.getXML_Position() + ')')

    def print_warning(self, msg):
        self.logger.warning(msg +' (' + self.getXML_Position() + ')')

    def _evaluateInput(self, variable):
        if type(variable) is not str:
            return variable
        result = ''
        for index, element in enumerate(variable.split('`')):
            if index % 2 == 1:
                evaluation = None
                error      = None
                try:
                    evaluation = eval(element)
                except:
                    pass
                if evaluation == None:
                    try:
                        import subprocess
                        proc = subprocess.Popen(element, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                        (out, err) = proc.communicate()
                        out = out.decode('UTF-8')
                        if out.strip() != '':
                            evaluation = out
                    except:
                        pass
                if evaluation == None:
                    message = 'invalid evaluation of `' + element + '`'
                    if err is not None:
                        message = message + ' (' + err.decode('UTF-8').strip() + ')'
                    self.print_warning(message)
                    evaluation = '`' + element + '`'
                if isinstance(evaluation, str):
                    element = evaluation.strip()
                else:
                    element = str(evaluation)
            result += element
        return result

    def getBoolean(self, value):
        value = value.lower()
        if value == 1 or value == 'true' or value == 'on':
            return True
        return False

    def _getNumber(self, string, evaluate = True):
        number = None
        try:
            return int(string)
        except ValueError:
            pass
        try:
            return float(string)
        except ValueError:
            pass
        if (number == None) and (evaluate):
            evaluation = self._evaluateInput(string)
            return self._getNumber(evaluation, False)
        self.raise_error(string + ' is not a number')

    def getVector(self, vector, size, none_value = None):
        if isinstance(vector, str):
            result = []
            for coordinate in vector.split(','):
                result.append(self._getNumber(coordinate))
        elif isinstance(vector, xml.sax.xmlreader.AttributesImpl) or isinstance(vector, dict):
            result = [None, None, None, None]
            for index, component in enumerate(['x', 'y', 'z', 'w']):
                if component in vector:
                    result[index] = self._getNumber(vector[component])
                else:
                    result[index] = none_value
        else:
            self.raise_error(str(vector) + ' is not or does not contain a vector !')
        if len(result) > size:
            result = result[:size]
        return result

    def _getChildren(self, name, attrs):
        return XML(self, name, attrs)

    def _default(self):
        pass

    def _recursiveEvaluation(self, variable):
        if type(variable) is dict:
            values = {}
            for name, value in variable.items():
                values[name] = self._recursiveEvaluation(value)
            return values
        if type(variable) is list:
            values = []
            for value in variable:
                values.append(self._recursiveEvaluation(value))
            return values
        if type(variable) is str:
            variable = self._evaluateInput(variable)
            try:
                return int(variable)
            except ValueError:
                pass
            try:
                return float(variable)
            except ValueError:
                pass
        return variable

    def getConfiguration(self):
        if hasattr(self, '_updateFromParents') and hasattr(self._updateFromParents, '__call__'):
            self._updateFromParents()
        self._default()
        result = {}
        for attribute_name in self._attribute_list:
            if (not hasattr(self, '_' + attribute_name)) or (getattr(self, '_' + attribute_name) is None):
                self._getChildren(attribute_name, {})
            attribute = self._recursiveEvaluation(getattr(self, '_' + attribute_name))
            self._attributs_inheritance[attribute_name] = attribute
            result[attribute_name] = attribute
        for class_name in self._class_list:
            if (not hasattr(self, '_' + class_name)) or (getattr(self, '_' + class_name) is None):
                self._getChildren(class_name, {})
            classes = getattr(self, '_' + class_name)
            if type(classes) is dict:
                result[class_name] = {}
                for name, obj in classes.items():
                    obj._attributs_inheritance = self._attributs_inheritance
                    result[class_name][name] = obj.getConfiguration()
            elif type(classes) is list:
                result[class_name] = []
                for obj in classes:
                    obj._attributs_inheritance = self._attributs_inheritance
                    result[class_name].append(obj.getConfiguration())
            elif classes is not None:
                classes._attributs_inheritance = self._attributs_inheritance
                result[class_name] = getattr(self, '_' + class_name).getConfiguration()
        return result

    def is_exe(self, filename):
        return os.path.isfile(filename) and os.access(filename, os.X_OK)

    def which(self, filename):
        if os.environ.get("PATH") is not None:
            locations = os.environ.get("PATH").split(os.pathsep)
            candidates = []
            for location in locations:
                candidate = os.path.join(location, filename)
                if self.is_exe(candidate):
                    return candidate
        return None

    def _setEnvironment(self, string):
        if self._environments is None:
            self._environments = {}
        for environment in self._evaluateInput(string).split("\n"):
            environment = environment.strip().split('=')
            if len(environment) > 1:
                self._environments[environment[0]] = ''.join(environment[1:])

class single(XML):
    def __init__(self, parent, name, attrs):
        super(single, self).__init__(parent, name, attrs)
        self._inside  = None

    def startElement(self, name, attrs):
        if name == self._inside:
            self.raise_error('Cannot define ' + name + ' section inside ' + self._inside)
        if self._inside is not None:
            self.raise_error(self._inside + ' section must not have children')
        self._inside = name

    def endElement(self, name):
        if self._inside == name:
            self._inside = None;
        elif name == self._xml_section_name:
            super(single, self).endElement(name)

    def characters(self, string):
        pass

class mono(XML):
    def __init__(self, parent, name, attrs):
        super(mono, self).__init__(parent, name, attrs)
        self._inside  = None

    def startElement(self, name, attrs):
        self.raise_error(self._xml_section_name + ' section must not have any children')

    def endElement(self, name):
        super(mono, self).endElement(name)

    def characters(self,string):
        pass
