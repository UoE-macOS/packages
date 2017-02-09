#!/bin/bash
#
# Generic package preinstall check (Updated 22.12.15).


# The environment variable $1 is the full path to the package. This means we can 
# programmatically get the name of the package and the version. awk with the delimiter 
# of a - will show the version and basename gets the final part of a path, so will
# display the name of the package.

PkgName=`basename $1`
PkgVersion=`echo $1 | awk -F "-" '{print $2}'`

# Interrogate the package using pkgutil to find out what application the package is
# installing. It would be possible to add an additional grep -v "XXXX.app" to ignore a 
# particular application.

AppPath=`pkgutil --payload-files $1  | grep ".app" | grep -v "/Contents" | grep -v "._"`
AppPathFix=`echo $AppPath | sed 's/^[./] *//g'` # Remove leading .
AppName=`basename "$AppPath"`

# Find the currently-installed version of the app. Not all applications have the 
# "CFBundleShortVersionString" key, where this isn't available use "CFBundleVersionString".
AppVersion=`defaults read "${AppPathFix}/Contents/Info" CFBundleShortVersionString`

# In case one or both version numbers are in the format N.N.N, the following commands make both
# the install package version and the currently-installed app version into unary numbers by
# removing the second decimal point in order to make the Check_Version comparison much simpler.
# If a version is in the format N.N, the $3 doesn't exist, so is simply ignored.

PkgVersionUnary=`echo "$PkgVersion" | awk -F "." '{print $1 "." $2$3}'`
AppVersionUnary=`echo "$AppVersion" | awk -F "." '{print $1 "." $2$3}'`

# Check whether the software being installed is currently running on the target Mac.

Check_Running ()
{
# To find if the app is running, use:
ps -A | grep "${AppName}" | grep -v "grep" > /tmp/RunningApps.txt

if grep -q $AppName /tmp/RunningApps.txt;
then
	echo "******Application is currently running on target Mac. Installation of "${PkgName}" cannot proceed.******"
	exit 1;
else
    echo "******Application is not running on target Mac. Proceeding...******"
    exit 0
fi
}

# Compare the version of the install package to the currently-installed app and fail if the same or older.

Check_Version ()
{
if [ $(echo "${PkgVersionUnary} = ${AppVersionUnary}" ) ] || [ $(echo "${PkgVersionUnary} > ${AppVersionUnary}" | bc ) -ne 1 ]
then
    touch /Library/MacMDP/Receipts/${PkgName}.mdpreceipt
	echo "******The installation package is at version "$PkgVersion" and the currently-installed app is at version "$AppVersion". This installation "${PkgName}" cannot continue******"
	exit 1;
else
	echo "******The app is either not installed on the target Mac or is at an older version than the install package. Proceeding with installation...******"
	Check_Running
	exit 0;
fi
}

Check_Version

exit 0;