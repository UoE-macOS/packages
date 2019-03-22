#!/bin/bash
set -eux -o pipefail


RELEASE=1
BUILD='_build'

PRODUCT=${1}
VERSION=${2}

if [ -z $1 ] || [ -z $2 ]
then
    echo "Usage: $0 [logic | garageband] version"
    exit 255
fi

[ -d "${BUILD}" ] && rm -r ${BUILD}
mkdir ${BUILD}

sed -e "s/XX_PRODUCT_XX/$PRODUCT/g" scripts/postinstall.tmpl > scripts/postinstall
chmod +x scripts/postinstall

pkgbuild --nopayload --version ${VERSION} --id com.github.uoe-macos.$PRODUCTextracontent --scripts scripts "${BUILD}/ExtraContent_product_NetInstall-${VERSION}-${RELEASE}.pkg"

