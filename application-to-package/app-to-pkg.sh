#!/bin/bash
#
#

echo "Drag the application (Application.app) and the directory containing scripts (preinstall and postinstall) that you want to package."

PACKAGE_ROOT="/tmp/build"
rm -dfR "${PACKAGE_ROOT}"
mkdir "${PACKAGE_ROOT}"

OUTPUT="/Users/Shared"

APPLICATION_TEST1=`echo $1 | grep ".app"`
APPLICATION_TEST2=`echo $2 | grep ".app"`

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
if [ -z "$APPLICATION_TEST1" ] && [ -z "$APPLICATION_TEST2" ]; then
	echo "No Application found!"
fi

cp -R "${APPLICATION_PATH}" "${PACKAGE_ROOT}"

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

if [ -e "${OUTPUT}/${APPLICATION_NAME}-${APPLICATION_VERSION}-1.pkg" ]; then
	mv -f "${OUTPUT}/${APPLICATION_NAME}-${APPLICATION_VERSION}-1.pkg" "${OUTPUT}/${APPLICATION_NAME}-${APPLICATION_VERSION}-1.old.pkg"
fi

/usr/bin/pkgbuild --identifier "ed.is.${APPLICATION_NAME}" --version "${APPLICATION_VERSION}" --install-location /Applications --scripts "${SCRIPT_PATH}" --root "${PACKAGE_ROOT}" "${OUTPUT}"/"${APPLICATION_NAME}-${APPLICATION_VERSION}-1.pkg"

rm -dfR "${PACKAGE_ROOT}"

exit 0;
