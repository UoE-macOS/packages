#!/bin/sh

set -eux -o pipefail

version=5.1.001.0
release=1

[ ! -d '_build' ] && mkdir '_build'

chmod +x Scripts/postinstall

pkgbuild --nopayload --scripts=Scripts --version=${version} --id uk.ac.ed.eca.fiery_bidi_patch ./_build/FieryBiDiPatch-${version}-${release}.pkg
