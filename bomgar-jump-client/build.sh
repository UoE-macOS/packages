#!/bin/sh

# This script will package the bomgar installer with a preinstall
# script to remove any existing instances.

if [ "${1}" == '-release' ]
then 
  release=${2}
else
  release='1.uoe'
fi

/bin/echo -n "Enter the path to the Bomgar Jump Client disk image: "
read dmg

if [ ! -f ${dmg} ]
then
  echo "Not a file: ${installer}"
  exit 255
fi

tmp=$(mktemp -d $TMPDIR/package-bomgar.XXXX)

mkdir -p "${tmp}/private/tmp"

cp -r ${dmg} "${tmp}/private/tmp/"

mount=$(hdiutil attach "${dmg}" -nobrowse | awk '/Apple_HFS/ {print $3}') 

version=$(defaults read ${mount}/Double-Click\ To\ Start\ Support\ Session.app/Contents/Info.plist  CFBundleVersion)

hdiutil detach ${mount}

# Make sure our scripts are executable - pkgbuild doesn't do this
chmod +x Scripts/{preinstall,postinstall}

pkgbuild --scripts Scripts --root ${tmp} --id uk.ac.ed.is.bomgar --version ${version} BomgarJumpClient-${version}-${release}.pkg

rm -r ${tmp}




