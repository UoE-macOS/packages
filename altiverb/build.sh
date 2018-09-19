#!/bin/sh
  
set -x
build_dir='_build'

VERSION=7.3.6
RELEASE=1

INSTALLER=Altiverb-${VERSION}-Mac-Installer

[ -d ${build_dir} ] && rm -r "${build_dir}"

mkdir ${build_dir}

# Download the installer
curl http://37.97.231.114/download/Altiverb%207/${INSTALLER}.zip > ${build_dir}/${INSTALLER}.zip

unzip -o -d scripts/ ${build_dir}/${INSTALLER}.zip

chmod +x scripts/postinstall

pkgbuild --nopayload --id com.audioease.altiverb --version $VERSION --scripts scripts ${build_dir}/AltiVerb-${VERSION}-${RELEASE}.pkg


