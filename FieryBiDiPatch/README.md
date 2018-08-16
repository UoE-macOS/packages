Readme
======

Run build.sh to create a package which will patch the Fiery 78xx PDE (version 5.1.001.0 only).

The patch modified a single byte in the isJobComple() function, to cause it to return immediately 
rather than querying cups until timeout. 

More info to come...
