#!/bin/bash

###################################################################
#
# This script attempts to verify whether Unity is correctly licensed
# and license it if not. 
# 
# This script assumes it is being run as a login hook by Jamf Pro: as
# such it expects arg3 to be the username of the logging-in user and 
# the licensing data to be passed in args 4, 5 and 6.
#
# Date: "Thu Sep 27 12:58:59 2018 +0100"
# Version: 0.0.2
# Origin: https://github.com/UoE-macOS/packages
# Released by JSS User: glee1
#
##################################################################
set -euo pipefail 

USER="${3}"
SERIAL="${4}"
USERNAME="${5}"
PASSWORD="${6}"

UNITY_PATH='/Applications/Unity/Unity.app/Contents/MacOS/Unity'
LICENSE_PATH='/Library/Application Support/Unity/'
LICENSE_FILE='Unity_lic.ulf'

function set_prefs(){
	# Try to get around unity's default behaviour 
    # of creating new projects in the root of the user's
    # home directory. Unfortunately tildae expansion doesn't 
    # seem to work on these paths so we need to blat them
    # in at login.
    defaults write /Users/$USER/Library/Preferences/com.unity3d.UnityEditor5.x.plist kNewProjectsPath "/Users/$USER/Documents"
    defaults write /Users/$USER/Library/Preferences/com.unity3d.UnityEditor5.x.plist kProjectBasePath "/Users/$USER/Documents/New Unity Project"
    defaults write /Users/$USER/Library/Preferences/com.unity3d.UnityEditor5.x.plist kWorkspacePath "/Users/$USER/Documents"
    
    # These could probably be done by other means, but since we are here, 
    # disable auto-upadte checking and remove the login screen on startup
    defaults write /Users/$USER/Library/Preferences/com.unity3d.UnityEditor5.x.plist EditorUpdateShowAtStartup -int 0
    defaults write /Users/$USER/Library/Preferences/com.unity3d.UnityEditor5.x.plist UnityConnectWorkOffline -int 1
    chown $USER /Users/$USER/Library/Preferences/com.unity3d.UnityEditor5.x.plist
}

if [ -f "${LICENSE_PATH}/${LICENSE_FILE}" ]
then
    echo "$0: Unity License file is already present. Exiting"
    set_prefs
    exit 0
fi

echo "$0: No Unity license file found. Continuing"
echo "$0: Running Unity licensing command."

# Create a temporary directory to work in: running this command seems 
# to spew ome stuff into the current working directory when Unity starts up.
tmpdir="$(mktemp -d /tmp/unitylicense.XXXX)"

# We are going to run unity as the logging-in user, so make sure
# they can write to our working directory
chmod 777 "${tmpdir}"

# CD
pushd "${tmpdir}"

# Run the licensing command
command="${UNITY_PATH} -quit -batchmode -serial ${SERIAL} -username ${USERNAME} -password ${PASSWORD}"

command_result=0
sudo -u $USER ${command} || command_result=1

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
        # Make sure the license file is writable by everyone, otherwise
		# unity complains on launch. It seems to want to update a timestamp
		chmod 666 "${LICENSE_PATH}/${LICENSE_FILE}"
        set_prefs
        exit 0
    else
        echo "$0: There is no license file, something went wrong"
        exit 1
    fi
else 
    echo "$0: Licensing command failed."
    exit 1
fi


