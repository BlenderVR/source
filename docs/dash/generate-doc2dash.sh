#!/bin/bash

user=dfelinto
server=dalaifelinto.com
path=/var/www/feeds/
upload=1

cd ..

echo "Building docs ..."
make html > /dev/null

echo "Building Dash docset ..."
doc2dash -A ./build/html -n Blender-VR -i dash/logo.png --force -I index.html > /dev/null

if [ $upload -eq 1 ]; then
  echo "Compacting docset ..."
  tar --exclude='.DS_Store' -cvzf BlenderVR.tgz $HOME/Library/Application\ Support/doc2dash/DocSets/Blender-VR.docset 1> /dev/null 2> /dev/null

  echo "Upload docset ..."
  scp BlenderVR.tgz $user@$server:$path
  rm BlenderVR.tgz

  echo "Docset uploaded to ${user}@${server}:${path}BlenderVR"
fi

