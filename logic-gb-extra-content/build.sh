#!/bin/bash
set -e -o pipefail


BUILD='_build'

if [ -z $1 ]
then
    echo "Usage: $0 version"
    exit 255
fi

VERSION=${1}

[ -d "${BUILD}" ] && rm -r ${BUILD}
mkdir ${BUILD}

chmod +x scripts/postinstall

# fetch the latest version of Carl's great script
curl 'https://raw.githubusercontent.com/carlashley/appleloops/master/appleLoops.py' > scripts/appleloops.py


pkgbuild --nopayload --version ${VERSION} --id com.github.uoe-macos.appleloops.deploy --scripts scripts "${BUILD}/AppleLoops_NetInstall-${VERSION}.pkg"

