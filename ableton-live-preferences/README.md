Ableton Live Shared Preferences
===============================

Use this script to build a package which contains the `Library.cfg` and `Options.cfg` files that are needed to get Live to behave sensibly in a multiuser environment.

See [https://help.ableton.com/hc/en-us/articles/209775405-Centralized-administration-of-Live-in-a-multi-user-environment-with-Sassafras-]

We set the following options in Options.cfg:

`-LicenseServer
-DontAskForAdminRights
-EventRecorder=Off
-_DisableAutoUpdates
-_DisableUsageData`

And we set up `Library.cfg` so that Live Packs are looked-for in `/Users/Shared/Ableton/Live Packs`.

Usage
=====

`./build.sh` 

To build a package which installs the preferences to the appropriate shared location. 