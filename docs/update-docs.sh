#!/bin/sh
sphinx-apidoc -o modules/rst/ ../modules/blendervr/ -f -e
sphinx-apidoc -o utils/rst ../utils/ -f -e
make html
