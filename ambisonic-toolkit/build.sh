#!/bin/sh

set -xeu

VERSION="1.0b10"
RELEASE=1
build="_build"

ATK_DATA="Library/Application Support/ATK"
USER_TEMPLATE="System/Library/User Template/Non_localized/Library/Application Support/REAPER"

[ -d ${build} ] && rm -r ${build}
mkdir ${build}

curl 'https://uc40735bc46033fd8f972c8e40dd.dl.dropboxusercontent.com/cd/0/get/AQ8pe_SaJHPd6tNzMyXRKaINT8Wju8aTyHT3jwiTNe6xT2s6dtVfg2a2FK4iFEah6X9a_nrOnNj8D-Ceneys4LeY7X7Y3tsgFfUn1sZmvawq5DZWykQmuyykEXFJ53rtyKWiBIxEtLhGXAsy05fYvCRvdP2KTojSZeNqeeLA34BWcS511WqzG8tTFDIzBb73mkk/file?_download_id=67509276180430747432948095779541883546864561352730273831769662096&_notify_domain=www.dropbox.com&dl=1' > ${build}/atk-$VERSION.zip

unzip -d ${build} ${build}/atk-$VERSION.zip

mkdir -p "${build}/pkgroot/${ATK_DATA}"
mkdir -p "${build}/pkgroot/${USER_TEMPLATE}"
mkdir "${build}/pkgroot/${USER_TEMPLATE}/presets"
mkdir "${build}/pkgroot/${USER_TEMPLATE}/Effects"
mkdir "${build}/pkgroot/${USER_TEMPLATE}/ColorThemes"
mkdir "${build}/pkgroot/${USER_TEMPLATE}/Data"

cp -R "${build}/ATK for Reaper/Copy content to presets/" "${build}/pkgroot/${USER_TEMPLATE}/presets/"
cp -R "${build}/ATK for Reaper/Copy content to Effects/" "${build}/pkgroot/${USER_TEMPLATE}/Effects/"
cp -R "${build}/ATK for Reaper/Copy content to ColorThemes/" "${build}/pkgroot/${USER_TEMPLATE}/ColorThemes/"
cp -R "${build}/ATK for Reaper/Copy content to Data/ATK/" "${build}/pkgroot/${ATK_DATA}/"

ln -s "/${ATK_DATA}" "${build}/pkgroot/${USER_TEMPLATE}/Data/ATK"

pkgbuild --root ${build}/pkgroot --id net.ambisonictoolkit.atk-reaper --version 1.0b10 ${build}/AmbisonicToolkitForREAPER-${VERSION}-${RELEASE}.pkg


