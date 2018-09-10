#!/bin/bash
set -eux -o pipefail

VERSION=1.0.0
RELEASE=1
BUILD='_build'

[ -d "${BUILD}" ] && rm -r ${BUILD}
mkdir ${BUILD}

# Fix up icons, which don't survive the transition to Git inside xattrs
dest="${BUILD}/root/Library/MacSD/weblocs"
mkdir -p "${dest}"

cp weblocs/*.url "${dest}"

ls "${dest}" | while read file
do
    file="${file%.*}"
    cmd="import Cocoa; Cocoa.NSWorkspace.sharedWorkspace().setIcon_forFile_options_(
        Cocoa.NSImage.alloc().initWithContentsOfFile_('icons/${file}.icns'), '${dest}/${file}.url', 0)"

    python -c "${cmd}"
    sleep 5
done

pkgbuild --version ${VERSION} --id uk.ac.ed.macsd.weblocs --root ${BUILD}/root "${BUILD}/MacSDWeblocs-${VERSION}-${RELEASE}.pkg"

lsbom $(pkgutil --bom "${BUILD}/MacSDWeblocs-${VERSION}-${RELEASE}.pkg")
