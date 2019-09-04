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
# Date: @@DATE
# Version: @@VERSION
# Origin: @@ORIGIN
# Released by JSS User: @@USER
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
LAUNCHAGENT_PATH='/Library/LaunchAgents/uk.ac.ed.eca.unity_license.plist'

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
    echo "$0: Unity License file is already present."
    # Current serial number lives in a base64-encoded string inside the license file
    if [ `xmllint --xpath 'string(//License/DeveloperData/@Value)' "${LICENSE_PATH}/${LICENSE_FILE}" | base64 -D | cut -c 5-` == "${SERIAL}" ]
    then
        echo "$0: Serial in <DeveloperData> matches current serial - exiting"
        set_prefs
        exit 0
    else
        # Move old license file out of the way, as we need to update the serial
        echo "$0: Serial in <DeveloperData> does not match current. Need to update."
        mv "${LICENSE_PATH}/${LICENSE_FILE}" "${LICENSE_PATH}/${LICENSE_FILE}".$(date "+%Y-%m-%d%n")
    fi
fi

echo "$0: Running Unity licensing command."

# Make sure the current user can write to Unity's Application Support folder
chmod 777 "${LICENSE_PATH}"

# Create a temporary directory to work in: running this command seems 
# to spew ome stuff into the current working directory when Unity starts up.
tmpdir="$(mktemp -d /tmp/unitylicense.XXXX)"

# We are going to run unity as the logging-in user, so make sure
# they can write to our working directory
chmod 777 "${tmpdir}"

# Define a launchAgent that will do our dirty work for us
launchagent_text="$(cat <<EOT
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key>
	<string>uk.ac.ed.eca.unity_license</string>
	<key>ProgramArguments</key>
	<array>
		<string>${UNITY_PATH}</string>
		<string>-quit</string>
		<string>-batchmode</string>
		<string>-serial</string>
		<string>${SERIAL}</string>
		<string>-username</string>
		<string>${USERNAME}</string>
		<string>-password</string>
		<string>$(python -c "from xml.sax.saxutils import escape; print escape('${PASSWORD}')")</string>
	</array>
    <key>WorkingDirectory</key>
    <string>${tmpdir}</string>
	<key>KeepAlive</key>
	<false/>
	<key>Enabled</key>
	<true/>
	<key>RunAtLoad</key>
	<true/>
</dict>
</plist>
EOT)"

# Create the launchagent
echo "${launchagent_text}" > "${LAUNCHAGENT_PATH}"

# And Launch it, in the current user's session
launchctl bootstrap gui/$(id -u ${USER}) "${LAUNCHAGENT_PATH}"
launchctl kickstart gui/$(id -u ${USER})/uk.ac.ed.eca.unity_license
sleep 10

command_result=$?

# Clean up our temporary directory and LaunchAgent 
rm -r "${tmpdir}"
rm "${LAUNCHAGENT_PATH}"

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


