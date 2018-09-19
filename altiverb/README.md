Package AltiVerb
================

The build script will create a package which can install AltiVerb solemtly in the background. The vendor package requires a GUI to run, and the script `scripts/install_script.tmpl` is the command that the GUI installer actually runs to do the installation.

An iLok is required for licensing.

# Build

`sh ./build.sh`

# Notes

This script is possibly quite version dependent. Care should be taken to check that the resultant package installs everything you expect.
