#!/bin/bash
set -eu -o pipefail

VERSION=1.0.0
RELEASE=1
DIR='_build'

[ -d "${DIR}" ] && rm -r ${DIR}
mkdir ${DIR}

pkgbuild --version ${VERSION} --id uk.ac.ed.macsd.weblocs --root root "${DIR}/MacSDWeblocs-${VERSION}-${RELEASE}.pkg"
