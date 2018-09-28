#!/bin/sh

VERSION="2018.1.1.6727"
RELEASE="1.eca"

python ./install-wwise.py \
       --install-prefix _build/root \
       --download-dir _build/Downloads

pkgbuild --root _build/root \
         --version ${VERSION} \
         --id com.audiokinetic.wwise \
         _build/Wwise-$VERSION-$RELEASE.pkg
