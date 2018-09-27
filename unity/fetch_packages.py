#!/usr/bin/env python
from __future__ import print_function
import urllib2
import shutil
import os
import unitylts

OUTPUT='./_build'

def main():
    if not os.path.isdir(OUTPUT):
        os.mkdir(OUTPUT)

    latest = unitylts.get_unity_lts_release(release='latest')

    for package in latest['files']:
        out = OUTPUT + '/' + package.split('/')[-1]
        if not os.path.isfile(out):
            print("Downloading ", package)
            fetch(package, out)
        else:
            print("Exists: ", out)


def fetch(url, output):
    """ Fetch `package` and store it in `dest`
    """
    try:
        resp = urllib2.urlopen(url)
        with open(output, 'wb') as fp:
            shutil.copyfileobj(resp, fp)
    except urllib2.HTTPError as err:
        print("Failed downloading {}: {}".format(url, err))


if __name__ == '__main__':
    main()





