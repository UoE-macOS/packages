#!/bin/bash
set -eux -o pipefail

VERSION=1040.0.0
RELEASE=1
BUILD='_build'

[ -d "${BUILD}" ] && rm -r ${BUILD}
mkdir ${BUILD}

chmod +x scripts/postinstall

pkgbuild --nopayload --version ${VERSION} --id com.github.uoe-macos.logicproextracontent --scripts scripts "${BUILD}/LogicProXExtraContent_NetInstall-${VERSION}-${RELEASE}.pkg"

