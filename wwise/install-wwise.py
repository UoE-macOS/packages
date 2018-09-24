#!/usr/bin/env python
from __future__ import print_function
import subprocess
import argparse
import json
import getpass
import urllib2
import shutil
import sys
import os
from base64 import b64decode

DESCRIPTION = 'Download and install some bundle of WWise'
VERSION = '0.0.1'


def process_args(argv=None):
    """Process any commandline arguments"""
    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     version=VERSION)

    parser.add_argument('--bundle',
                        dest='BUNDLE', default='2018.1.1_6727', help=(('ID of the bundle that you want to build '
                                                                       'defaults to 2018.1.1_6727')))
    parser.add_argument('--email', default=False,
                        dest='EMAIL', help=('Wwise account email address.'))

    parser.add_argument('--password', default=False,
                        dest='PASSWORD', help=('Wwise account password (you wll be prompted if missing)'))

    parser.add_argument('--install', default='mini',
                        dest='STYLE', help=('Install Style. mini or maxi'))

    parser.add_argument('--download-dir', default='/Library/Application Support/Wwise/Downloads',
                        dest='DOWNLOAD_DIR', help=('Directory to download installation files to'))

    parser.add_argument('--install-dir', default='/Applications',
                        dest='INSTALL_DIR', help=('Directory to install to'))

    args = parser.parse_args(argv)

    if not args.EMAIL:
        print("You must specify at least an email address")
        return False
    if not args.PASSWORD:
        args.PASSWORD = getpass.getpass(
            prompt='Password for {}: '.format(args.EMAIL), stream=None)

    return args


def main(args):
    BUNDLE_YEAR = args.BUNDLE.split('.')[0]

    URLBASE = 'https://www.audiokinetic.com/wwise/launcher/?action='

    CREDENTIALS = {
        "email": args.EMAIL,
        "password": args.PASSWORD,
    }

    LAUNCHER_DATA = {
        "launcher": {
            "version": {
                "year": 2018,
                "major": 9,
                "minor": 6,
                "build": 806
            },
            "platform": "osx"
        }
    }

    CONTEXT_DATA = {"context": {
        "version": 1
    }
    }

    ARCHIVES_APP = ['Wwise.app.zip']
    ARCHIVES_AUTHORING = ['Authoring.tar.xz',
                          'Authoring.x64.tar.xz', ]

    INSTALL_DIR = args.INSTALL_DIR + '/' + args.BUNDLE
    DOWNLOAD_DIR = args.DOWNLOAD_DIR + '/' + args.BUNDLE

    # Build our authentication blob
    auth_data = {}
    auth_data.update(CREDENTIALS)
    auth_data.update(LAUNCHER_DATA)

    # Authenticate
    resp = fetch(URLBASE + 'login', data=auth_data)

    # We get back a token called 'jwt' which has to be sent with subsequent requests
    jwt = decode_payload(resp.read())

    print(jwt)

    # The body of all subsequent POST requests has to contain the following information
    body = {}
    body.update(jwt)
    body.update(LAUNCHER_DATA)
    body.update(CONTEXT_DATA)

    # This file is enormous, and in practice we already know which bundle we want
    # resp = requests.post(urlbase+'allBundles', json=body)
    # bundles = decode_payload(resp.text)
    # print(bundles)

    # Download a JSON list of all the available files for this bundle
    resp = fetch(URLBASE + 'getFiles&bundle_id=' + args.BUNDLE, data=body)
    all_files = decode_payload(resp.read())

    if args.STYLE == 'mini':
        # Only install the app and required Authoring packages
        to_download = [f for f in all_files['files']
                       if f['name'] in (ARCHIVES_APP + ARCHIVES_AUTHORING)]
    else:
        to_download = all_files['files']

    if not os.path.isdir(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    for f in to_download:
        outfile = DOWNLOAD_DIR + "/" + f['name']
        if not (f.get('url', False)):
            print("{}: no URL.".format(outfile))
            continue

        if os.path.isfile(outfile):
            disk_size = os.path.getsize(outfile)
            download_size = f.get('size', 0)
            print("{}: disk: {}, server: {}".format(
                outfile, disk_size, download_size))
            if disk_size >= download_size:
                continue

        print("{}: Downloading.".format(f['url']))
        # Some content is served from a CDN which only permits GET requests.
        # urllib will only issue a GET request if the 'data' argument is missing.
        if f['url'].find('rackcdn') >= 0:
            fetch(f['url'], dest=DOWNLOAD_DIR + "/" + f['name'])
        else:
            fetch(f['url'], data=body, dest=DOWNLOAD_DIR + "/" + f['name'])

    # Install the application itself
    print("Unarchiving main application to {}".format(INSTALL_DIR))
    for arc in ARCHIVES_APP:
        unarchive(DOWNLOAD_DIR + '/' + arc, INSTALL_DIR)

    # Directory into which we need to install supporting files 
    support_files = INSTALL_DIR + ('/Wwise.app/Contents/SharedSupport/Wwise/support'
                                   '/wwise/drive_c/Program Files/Audiokinetic/Wwise')

    # Decompress the Authoring files.. these are required
    print("Installing authoring support to {}".format(support_files))
    for arc in ARCHIVES_AUTHORING:
        unarchive(DOWNLOAD_DIR + '/' + arc, support_files)

    # The wwise_launcher script handles te mechanics of launching the windows
    # executable under Wine. If it detects that the MS Visual C++ redistributable package
    # isn't installed, it will download it and run the installer. which is fine, but needs user
    # interaction for no good reason. We patch the launcher script to add the '\q' flag
    # to the installation command.
    print("Patching launcher for silent install of VCC redistributable")
    launcher = INSTALL_DIR + ('/Wwise.app/Contents/SharedSupport/'
                              'Wwise{}/Wwise{}/wwise_launcher').format(BUNDLE_YEAR, BUNDLE_YEAR)
    target = '"$WINE" --wait-children "$UNIX_C_DRIVE"/vc_redist.x64.exe'
    newstr = '"$WINE" --wait-children "$UNIX_C_DRIVE"/vc_redist.x64.exe "/q" "/norestart"'

    with open(launcher, 'r') as l:
        text = l.read().replace(target, newstr)

    with open(launcher, 'w') as l:
        l.write(text)

    print("Done")


def decode_payload(payload):
    parsed = json.loads(payload)
    decoded = b64decode(parsed.get('payload', None))
    return json.loads(decoded)


def unarchive(path, dest):
    if not os.path.isdir(dest):
        os.makedirs(dest)
    cmd = None
    if path.endswith('.tar.xz'):
        cmd = ['/usr/bin/tar', '-C', dest, '-xzf', path]
    elif path.endswith('.zip'):
        cmd = ['/usr/bin/unzip', '-q', '-d', dest, path]
    return subprocess.check_call(cmd)


def fetch(url, dest=None, data=None):
    """ Fetch `url`.
        If `data` is present send a POST request, otherwise GET
        If `dest` is present, store the result there, otherwise
        return a file-like object.
    """
    if data:
        # If data is serialisable, send it as json
        try:
            mydata = json.dumps(data)
        except:
            # Just send whatever we were passed, raw
            mydata = data
        resp = urllib2.urlopen(url, mydata)
    else:
        resp = urllib2.urlopen(url)
    if dest:
        with open(dest, 'wb') as fp:
            shutil.copyfileobj(resp, fp)
    else:
        return resp


if __name__ == '__main__':
    main(process_args())
