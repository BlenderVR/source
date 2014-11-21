#!/bin/sh

# generate the rst files
sphinx-apidoc -o modules/rst/ --force --separate --maxdepth=1 ../modules/blendervr/
sphinx-apidoc -o utils/rst --force --no-headings --separate --maxdepth=1 ../utils/

# remote the unused files
rm modules/rst/modules.rst
rm utils/rst/modules.rst

# compile the docs
make html
