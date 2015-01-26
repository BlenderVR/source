# -*- coding: utf-8 -*-
# file: blendervr/processor/__init__.py

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

"""
Handle all the processors, which are defined per project.

A processor is a python module that allows Blender-VR to run special
code for specific project.

It can, for example, load OSC modules, or link the HMD to the scene camera.
"""

import random
import copy
from .base import Processor

_processor_files = []
_main_logger = None
_debug_processor = False


def getProcessor():
    """
    Get the latest added ``Processor`` file.

    :rtype: ``Processor``
    """
    global _processor_files, _main_logger, _debug_processor
    import os

    if not _processor_files:
        return Processor
    processor_file = _processor_files.pop(0)

    if processor_file is None:
        _main_logger.warning('Empty processor file')
        return Processor

    module_path = os.path.dirname(processor_file)
    if not os.path.isdir(module_path):
        _main_logger.warning('Invalid path for processor: ', module_path)
        return Processor

    module_name = os.path.splitext(os.path.basename(processor_file))[0]
    try:
        import imp
        (file, file_name, data) = imp.find_module(module_name, [module_path])
    except:
        _main_logger.warning('Cannot import "' + module_name + '" module from "'
                        + module_path + '"')
        if _debug_processor:
            _main_logger.debug_processor(False)
        return Processor

    try:
        module = imp.load_module('processor_'
                + str(random.randrange(268431360)), file, file_name, data)
    except:
        _main_logger.warning('Invalid import of module "' + processor_file + '"')
        if _debug_processor:
            _main_logger.debug_processor(False)
        return Processor

    import inspect
    for name in dir(module):
        element = getattr(module, name)
        if inspect.isclass(element) and issubclass(element, Processor):
            _main_logger.info('Loading "' + name + '" class from "' + file_name
                         + '" as main processor')
            return element

    _main_logger.warning('Cannot import "' + str(Processor.__name__)
                    + '" class for logger from "' + file_name + '"')
    return Processor


def appendProcessor(processor_file):
    """
    Include the processor file to be executed.

    :param processor_file: Python file with the process functions for the
        application
    :type processor_file: string
    """
    global _processor_files
    _processor_files.insert(0, processor_file)


def _getProcessor(processor_files, main_logger, debug_processor):
    """
    Function called by the main process (Virtual environment or Console)
    Don't call it !
    """
    global _processor_files, _main_logger, _debug_processor

    random.seed()

    _processor_files = copy.copy(processor_files)
    _main_logger = main_logger
    _debug_processor = debug_processor

    return getProcessor()

