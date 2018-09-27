#!/bin/bash

###################################################################
#
# This script attempts to verify whether Unity is correctly licensed
# and license it if not. It needs to be run as root but also with a 
# user logged in (it uses the actual Unity application to perform the 
# licensing operation). 
# 
# This script assumes it is being run as a login hook by Jamf Pro: as
# such it expects arg1 to be the username of the logging-in user and 
# the licensing data to be passed in args 4, 5 and 6.
#
# Date: @@DATE
# Version: @@VERSION
# Origin: @@ORIGIN
# Released by JSS User: @@USER
#
##################################################################
set -euo pipefail

USER="${1}"
SERIAL="${4}"
USERNAME="${5}"
PASSWORD="${6}"

UNITY_PATH='/Applications/Unity/Unity.app/Contents/MacOS/Unity'
LICENSE_PATH='/Library/Application Support/Unity/'
LICENSE_FILE='Unity_lic.ulf'

if [ -f "${LICENSE_PATH}/${LICENSE_FILE}" ]
then
    echo "$0: Unity License file is already present. Exiting"
    exit 0
fi

echo "$0: No Unity license file found. Continuing"

# Make sure the license path isn't writable by mere mortals, otherwise
# users can inadvertantly relicense the app with their own login details.
chown root:admin "${LICENSE_PATH}"
chmod 755 "${LICENSE_PATH}"

echo "$0: Running Unity licensing command."

# CD to a temporary directory: running this command as root seems to spew
# some stuff into the current working directory when Unity starts up.
tmpdir="$(mktemp -d /tmp/unitylicense.XXXX)"
pushd "${tmpdir}"

# Run the licensing command
command="${UNITY_PATH} -quit -batchmode -serial ${SERIAL} -username ${USERNAME} -password ${PASSWORD}"

command_result=0
${command} || command_result=1

# Clean up our temporary directory
popd && rm -r "${tmpdir}"

# In some cases the above operation seems to create root-owned folders under
# the current user's /Library/Application Support/Unity folder. Make sure that, 
# if these now exist, they are permissioned correctly.
user_home="$(eval echo "~${USER}")"
if [ -d "${user_home}/Library/Application Support/Unity" ]
then
    chown -R ${USER} "${user_home}/Library/Application Support/Unity"
fi

# Now, assess whether we have been successful
if [ "${command_result}" == 0 ]
then
    if [ -f "${LICENSE_PATH}/${LICENSE_FILE}" ]
    then
        echo "$0: That seemed to work."
        exit 0
    else
        echo "$0: There is no license file, something went wrong"
        exit 1
    fi
else 
    echo "$0: Licensing command failed."
    exit 1
fi


