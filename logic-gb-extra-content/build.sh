#!/bin/bash
set -e -o pipefail


RELEASE=1
BUILD='_build'

if [[ $1 != 'logicpro' && $1 != 'garageband' ]] || [ -z $2 ]
then
    echo "Usage: $0 [logicpro | garageband] version"
    exit 255
fi

PRODUCT=${1}
VERSION=${2}

[ -d "${BUILD}" ] && rm -r ${BUILD}
mkdir ${BUILD}

sed -e "s/XX_PRODUCT_XX/$PRODUCT/g" scripts/postinstall.tmpl > scripts/postinstall
chmod +x scripts/postinstall

pkgbuild --nopayload --version ${VERSION} --id com.github.uoe-macos.${PRODUCT}_extracontent --scripts scripts "${BUILD}/ExtraContent_${PRODUCT}_NetInstall-${VERSION}-${RELEASE}.pkg"

