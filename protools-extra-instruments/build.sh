#!/bin/bash

file="ThisIsNotAFile"

while [[ ! -f $file ]]
do
  echo "Path to the AIR Instruments .dmg file"
  read file
done

cp "${file}" scripts/ProToolsExtraFirstAIRInstrumentsBundle.dmg

chmod +x scripts/postinstall
pkgbuild --id com.github.uoe-macos.protools_air_instruments --nopayload --scripts scripts --version 2018.4 ProToolsExtraFirstAIRInstrumentsBundle-2018.4-1.pkg

