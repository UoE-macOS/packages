#!/usr/bin/env python
""" Download all the packages associated with the letest LTS
    release of Unity. Uses 'unitylts.py' to work out which packages
    are required
"""
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
    """ Fetch `url` and store it in `output`
    """
    try:
        resp = urllib2.urlopen(url)
        with open(output, 'wb') as fp:
            shutil.copyfileobj(resp, fp)
    except urllib2.HTTPError as err:
        print("Failed downloading {}: {}".format(url, err))


if __name__ == '__main__':
    main()





