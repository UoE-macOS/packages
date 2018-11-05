#!/bin/sh

PKG_VERSION='1.0.0'
LIVE_VERSION='10.0.1'
PREFS_PATH="/Library/Preferences/Ableton/Live ${LIVE_VERSION}"


tmpdir="$(mktemp -d ableton.XXXX)"

mkdir -p "$tmpdir/pkgroot/$PREFS_PATH"

cp Library.cfg Options.txt "$tmpdir/pkgroot/$PREFS_PATH"

pkgbuild --root "$tmpdir/pkgroot/" --id uk.ac.ed.eca.ableton_live_prefs --version 1.0.0 _build/AbletonLivePreferences-${PKG_VERSION}-1.pkg

rm -r "${tmpdir}"