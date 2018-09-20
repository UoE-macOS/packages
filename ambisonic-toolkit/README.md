Re-package ambisonic toolkit for REAPER
=======================================

The Ambisonic Toolkit for REAPER wants to install its files to ~/Library. This is not good in a multi-user studio environment.

This script will build a package which installs most of the components into the Non-Localized User Template folder, but installs the (relatively large) convolution kernel data to `/Library/Application Support/ATK` and symlinks this to the user template. 

## Build

`sh ./build.sh`
