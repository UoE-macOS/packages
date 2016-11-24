#!/bin/bash
#
#
# This script will create a package according to our standard naming scheme.
# It can only be used to package ".app" items and if no scripts are provided will use the default.

echo "Drag the application (Application.app) and the directory containing scripts (preinstall and postinstall) that you want to package."

PACKAGE_ROOT="/tmp/build_folder"

# Path to this script
SCRIPT="${BASH_SOURCE[0]}";
# Path to the Resource folder
RESOURCE_DIR=`dirname "${SCRIPT}"`
DEFAULT_SCRIPTS=`echo "${RESOURCE_DIR}/Scripts"`

# Make a fresh package root
rm -dfR "${PACKAGE_ROOT}"
mkdir "${PACKAGE_ROOT}"

OUTPUT="/Users/Shared/App_to_Packages"
mkdir "${OUTPUT}"

APPLICATION_TEST1=`echo $1 | grep ".app"`
APPLICATION_TEST2=`echo $2 | grep ".app"`

if [ -z "$APPLICATION_TEST1" ] && [ -z "$APPLICATION_TEST2" ]; then
	echo "No Application found!"
else
	if [ -z "$APPLICATION_TEST1" ]; then
		APPLICATION_PATH="$2"
		if [ `ls "$1" | grep preinstall` ] || [ `ls "$1" | grep postinstall` ]; then
			SCRIPT_PATH="$1"
		fi
	fi
	if [ -z "$APPLICATION_TEST2" ]; then
		APPLICATION_PATH="$1"
		if [ `ls "$2" | grep preinstall` ] || [ `ls "$2" | grep postinstall` ]; then
			SCRIPT_PATH="$2"
		fi
	fi
	echo "Application path determined as $APPLICATION_PATH"
	
	if [ -z "$SCRIPT_PATH" ]; then
		SCRIPT_PATH="$DEFAULT_SCRIPTS"
		echo "No scripts provided using default."
	else
		echo "Script path determined as $SCRIPT_PATH"
	fi
fi

echo "Copying application to build location..." 
cp -R "${APPLICATION_PATH}" "${PACKAGE_ROOT}"

echo "Determining application name an version."
APPLICATION_NAME=`basename "$APPLICATION_PATH" | tr ' ' '-' | awk -F ".app" '{print $1}'`

BUNDLE_VERSION1=`defaults read "${APPLICATION_PATH}/Contents/Info" CFBundleShortVersionString`
BUNDLE_VERSION2=`defaults read "${APPLICATION_PATH}/Contents/Info" CFBundleVersionString`

if [ -z "$BUNDLE_VERSION1" ] && [ -z "$BUNDLE_VERSION2" ]; then
	echo "Application version has not been found, setting to 1.0"
	APPLICATION_VERSION="1.0"
else
	if [ -z "$BUNDLE_VERSION1" ]; then
		APPLICATION_VERSION="$BUNDLE_VERSION2"
	fi
	if [ -z "$BUNDLE_VERSION2" ]; then
		APPLICATION_VERSION="$BUNDLE_VERSION1"
	fi
fi

echo "Application name: $APPLICATION_NAME"
echo "Application version: $APPLICATION_VERSION"

if [ -e "${OUTPUT}/${APPLICATION_NAME}-${APPLICATION_VERSION}-1.pkg" ]; then
	mv -f "${OUTPUT}/${APPLICATION_NAME}-${APPLICATION_VERSION}-1.pkg" "${OUTPUT}/${APPLICATION_NAME}-${APPLICATION_VERSION}-1.old.pkg"
	echo "Previous package found and renamed: ${OUTPUT}/${APPLICATION_NAME}-${APPLICATION_VERSION}-1.old.pkg"
fi

/usr/bin/pkgbuild --identifier "ed.is.${APPLICATION_NAME}" --version "${APPLICATION_VERSION}" --install-location /Applications --scripts "${SCRIPT_PATH}" --root "${PACKAGE_ROOT}" "${OUTPUT}"/"${APPLICATION_NAME}-${APPLICATION_VERSION}-1.pkg" 2>&1

rm -dfR "${PACKAGE_ROOT}"

echo "Opening the output location; ${OUTPUT}"

open "${OUTPUT}"

echo "Process completed. Drag the application (Application.app) and the directory containing scripts (preinstall and postinstall) that you want to package or Quit.

exit 0;
