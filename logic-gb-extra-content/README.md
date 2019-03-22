Install Logic Pro X or GarageBand Extra Content
=================================

A package to download and install all of the Logic X Pro Extra or GarageBand Content direct from Apple's servers. 

# To Build
`sh build.sh [logicpro | garageband] version-release`

For example, to build a package with the extra content for Garageband, and give it version 1032-1, type:

`sh build.sh garageband 1032-1`

# Thanks

Thanks to https://github.com/hjuutilainen/ for the download script, which I've lightly modified to handle installation

and

Thanks to https://github.com/munki/ for FoundationPlist.py
