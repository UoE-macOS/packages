#!/usr/bin/python
""" Scrape the page at https://unity3d.com/unity/qa/lts-releases to
    determine the available Unity LTS releases and the files associated
    with them.

    This uses htmllib rather than bs4 to avoid non-stdlib dependencies.
    Because it's scraping a web page it is fragile. If the format of the
    page or the download page changes significantly it will break. YMMV.

    This is intended to be imported as a module like so:

    import unitylts

    latest = unitylts.get_unity_lts_release(release='latest')
    for package in latest['files']:
        download_or_something(package)

    You can also call it direct from the commandline to see the
    same information as is returned by the above function, like:

    ./unitylts.py [release]
"""

from __future__ import print_function
from HTMLParser import HTMLParser
import urllib2
from urlparse import urlsplit
import shutil
import sys
from distutils.version import LooseVersion

our_list = []
FEED_URL = 'https://unity3d.com/unity/qa/lts-releases'
FEED_HTML = "_build/lts-releases.html"


class MyHTMLParser(HTMLParser):
    """ HTML Parser class which does one thing only """

    def handle_starttag(self, tag, attrs):
        """ Search for 'a' tags which have an 'href' element that appears
            to be a unity download (and isn't a torrent). Pass them off to
            the _add_to_list function to be added to our list of releases
        """
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
    my_release = get_unity_lts_release(
        sys.argv[1] if 1 < len(sys.argv) else 'latest')
    print("Version: ", my_release['version'])
    print("Revision: ", my_release['revision'])
    for a_file in my_release['files']:
        print("Package:", a_file)
