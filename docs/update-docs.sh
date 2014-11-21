#!/bin/sh
sphinx-apidoc -o modules/rst/ --force --separate --maxdepth=1 ../modules/blendervr/
sphinx-apidoc -o utils/rst --force --no-headings --separate --maxdepth=1 ../utils/
make html
