IRCAM Forumnet Activation Package Builder
======================================

# Usage
`./build.sh path_to_license_file expiry_date

# Description
The IRCAM forumnet software is activated by passing a key file (received via email) to one of any of the commandline tools that make up the suite. This script will build a package which wraps the key file and a script to do the registration.

# Limitations
Key files are only valid for 14 days, so it is expected that you'll pass the expiry date as an argument so that it can be included in the package name. Packages used after their expiry date will not authorise the software.

The activation script relies on being able to find one of the IRCAM commandline tools to carry out authorisation. Since at the time of writing, AudioSculpt is the only tool we install, we look for one of its components. The script could easily be modified to look for something else.