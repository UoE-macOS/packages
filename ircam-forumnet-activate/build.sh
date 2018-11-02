#!/bin/sh

set -eu

KEY_FILE=${1}
EXPIRATION_DATE=${2}
VERSION='1.0.0'


if [ ! -f "${KEY_FILE}" ]
then
    echo "First argument must be the path to the Ircam key file"
    exit 255
fi

# Copy the key file into our Scripts folder temporarily
cp "${KEY_FILE}" ./scripts/Ircam_Activation_Key.txt

chmod +x ./scripts/postinstall

pkgbuild --nopayload --scripts ./scripts --id uk.ac.ed.ircam_activation --version $VERSION "_out/IrcamForumActivate_Expires_$EXPIRATION_DATE-$VERSION.pkg"

rm ./scripts/Ircam_Activation_Key.txt