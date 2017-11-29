# A package to randomise the root password on MacOS

This is intended to implement the workaround for the High Sierra blank password root login bug. 
The build script creates a package which can be given to users of unmanaged machines in order to protect themselves.

We set the root password to a long random string, and attempt to do so in a way which minimises the likelihood of the password being displayed anywhere.

## How to use it
To build a package:

```sh ./build.sh```

### Disclaimer
Use entirely at your own risk.
