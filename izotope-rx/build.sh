#!/bin/bash


BUILD='_build'

[ -d "${BUILD}" ] && rm -r ${BUILD}
mkdir ${BUILD}

file="ThisIsNotAFile"

while [[ ! -f $file ]]
do
  echo -n "Enter the path to the Izotope RX installation DMG: "
  read file
done

cp "${file}" scripts/IzotopeRX.dmg

chmod +x scripts/postinstall
pkgbuild --id com.izotope.rx --nopayload --scripts scripts --version 7.0.0 ${BUILD}/IzotopeRX-7.0.0-1.pkg

rm scripts/IzotopeRX.dmg

