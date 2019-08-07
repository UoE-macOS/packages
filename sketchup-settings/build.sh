#!/bin/sh

rm -rf _build &&  mkdir _build
pkgbuild --id com.guthub.uoe-macos.sketchup-settings --version 2019.08 --root ./root _build/Sketchup2019Settings-2019.08.pkg

lsbom `pkgutil --bom _build/Sketchup2019Settings-2019.08.pkg`


