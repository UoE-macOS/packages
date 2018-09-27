#!/usr/bin/python
from __future__ import print_function
from HTMLParser import HTMLParser
import urllib2
from urlparse import urlparse, urlsplit
import shutil
import sys
import re
from pprint import pprint
from distutils.version import LooseVersion

our_list = []
FEED_URL = 'https://unity3d.com/unity/qa/lts-releases'
FEED_HTML = "_build/lts-releases.html"


class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if (attr[0] == 'href' and
                    attr[1].find('download_unity') >= 0 and
                        not attr[1].find('torrent') > 0):
                    _add_to_list(attr[1])


def _add_to_list(url):
    rev = _get_rev(url)
    ver = _get_ver(url)
    entry = [v for v in our_list if v['version'] == ver]
    if entry and entry != []:
        entry[0]['files'].append(url)
    else:
        our_list.append({'version': ver, 'revision': rev, 'files': [url]})


def _get_rev(url):
    u = urlsplit(url)
    return u.path.split('/')[2]


def _get_ver(url):
    u = urlsplit(url)
    v = u.path.split('/')[-1].split('-')[-1].split('.')[:-1]
    return '.'.join(v)


def _get_latest():
    latest = '0.0.0'
    for rel in our_list:
        thisv = rel['version']
        if LooseVersion(thisv) > LooseVersion(latest):
            latest = thisv
    return latest


def get_unity_lts_release(release='latest'):
    """ Return a dict containing the attributes
        'version', 'revision', and 'files' 
        for the requested `release`. If `release` is 
        not specified, we return the latest we can find,
        as compared by distutils.version.LooseVersion
    """
    parser = MyHTMLParser()

    resp = urllib2.urlopen(FEED_URL)
    with open(FEED_HTML, 'wb') as fp:
        shutil.copyfileobj(resp, fp)

    parser.feed(open(FEED_HTML, 'r').read())

    if release == 'latest':
        search_for = _get_latest()
    else:
        search_for = release

    found = [v for v in our_list if v['version'] == search_for]
    
    if found != []:
        return found[0]
    else:
        return None

if __name__ == "__main__":
    pprint(get_unity_lts_release(sys.argv[1] if 1 < len(sys.argv) else 'latest') or 'Release not found')