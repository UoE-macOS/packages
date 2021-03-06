#!/bin/bash

set -euo pipefail

VERSION=1.0.1
RELEASE=1

package=""
echo "Enter path to quickadd package:"
read package
while [ ! -f ${package} ]
do
    read package
done

rm -rf _build
mkdir _build

tmpdir=$(mktemp -d /tmp/cleanbuild-pkg.XXXX)

mkdir -p ${tmpdir}/root/Library/MacSD

cp ${package} ${tmpdir}/root/Library/MacSD

chmod +x Scripts/*

pkgbuild --root ${tmpdir}/root --scripts ./Scripts --id uk.ac.ed.eca.ECACleanBuildAndEnrol --version ${VERSION} _build/ECACleanBuildAndEnrol-${VERSION}-${RELEASE}.pkg

rm -r ${tmpdir}
