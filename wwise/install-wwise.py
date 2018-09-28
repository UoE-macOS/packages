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

DESCRIPTION = ('Emulate the Wwise Launcher application to download and install '
               'the desired version of the Wwise app. Also patches the installed '
               'copy to remove the need for user interaction during the installation '
               'of the Visual C++ redistributable package which happens on 1st run.')

VERSION = '0.0.4'


def process_args(argv=None):
    """Process any commandline arguments"""
    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     version=VERSION)

    parser.add_argument('--bundle',
                        dest='BUNDLE', default='2018.1.1_6727', 
                        help=('ID of the bundle that you want to build '
                              'defaults to 2018.1.1_6727'))
    parser.add_argument('--email', default='',
                        dest='EMAIL', help=('Wwise account email address. '
                                            'Leave this unset for anonymous download.'))

    parser.add_argument('--password', default='',
                        dest='PASSWORD', 
                        help=('Wwise account password (you will be prompted if missing)'))

    parser.add_argument('--install', default='mini',
                        dest='STYLE', help=('Install Style. mini or maxi'))

    parser.add_argument('--download-dir', default='/Library/Application Support/Wwise/Downloads',
                        dest='DOWNLOAD_DIR', help=('Directory to download installation files to'))

    parser.add_argument('--install-prefix', default='/',
                        dest='INSTALL_PREFIX',
                        help=('Directory to install to. Wwise will be installed '
                              'to Applications/Audiokinetic/Wwise RELEASE/ under '
                              'this prefix. Defaults to "/" but you can use something '
                              'else to install into a temporary root for packaging.'))

    parser.add_argument('--real-install-prefix', default='/',
                        dest='REAL_PREFIX',
                        help=('If you plan to relocate the install (eg because you '
                              'are installing into a temporary package root), use this '
                              'argument to specify the final prefix on the front of '
                              '/Applications. Defaults to "/" and should be left unchanged '
                              'if you are building a package which will ultimately install '
                              'to /Applications.'))

    args = parser.parse_args(argv)

    # If an email has been set but not a password, prompt for the latter.
    if args.EMAIL != "" and args.PASSWORD == "":
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
                          'FilePackager.x64.tar.xz',
                          'Authoring.x64.tar.xz', ]

    INSTALL_PATH = 'Applications/Audiokinetic/Wwise ' + \
        args.BUNDLE.replace('_', '.')
        
    INSTALL_DIR = args.INSTALL_PREFIX + '/' + INSTALL_PATH

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
    bundle_data = decode_payload(resp.read())

    # Start to build the 'install-table.json' file which we will leave behind
    install_table = {'wwise.{}'.format(
        args.BUNDLE.replace('.', '_')): {
            'bundle': {},
            'children': [],
            'entryState': 0,
            'installed': {
                'date': {},
                'files': [],
                'groups': [],
            },
            'sampleFiles': [],
            'targetDir': args.REAL_PREFIX + INSTALL_PATH
    }
    }

    receipt = install_table['wwise.' + args.BUNDLE.replace('.', '_')]
    receipt['bundle'].update({'version': bundle_data['version']})
    receipt['bundle'].update({'id': bundle_data['id']})
    receipt['bundle'].update({'name': bundle_data['name']})
    receipt['bundle'].update(
        {'displayName': bundle_data['name'] + ' ' + args.BUNDLE})

    if args.STYLE == 'mini':
        # Only install the app and required Authoring packages
        to_download = [f for f in bundle_data['files']
                       if f['name'] in (ARCHIVES_APP + ARCHIVES_AUTHORING)]
    else:
        to_download = bundle_data['files']

    if not os.path.isdir(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    for candidate in to_download:
        outfile = DOWNLOAD_DIR + "/" + candidate['name']
        if not (candidate.get('url', False)):
            print("{}: no URL.".format(outfile))
            continue

        if os.path.isfile(outfile):
            disk_size = os.path.getsize(outfile)
            download_size = candidate.get('size', 0)
            print("{}: disk: {}, server: {}".format(
                outfile, disk_size, download_size))
            if disk_size >= download_size:
                continue

        print("{}: Downloading.".format(candidate['url']))
        # Some content is served from a CDN which only permits GET requests.
        # urllib will only issue a GET request if the 'data' argument is missing.
        if candidate.get('method', None) == 'GET':
            fetch(candidate['url'], dest=DOWNLOAD_DIR +
                  "/" + candidate['name'])
        else:
            fetch(candidate['url'], data=body,
                  dest=DOWNLOAD_DIR + "/" + candidate['name'])

     # Directory into which we need to install supporting files
    support_files = INSTALL_DIR + ('/Wwise.app/Contents/SharedSupport/Wwise/support'
                                   '/wwise/drive_c/Program Files/Audiokinetic/Wwise')

    # Install the application itself
    print("Unarchiving main application to {}".format(INSTALL_DIR))
    for arc in [f for f in bundle_data['files'] if f['name'] in ARCHIVES_APP]:
        unarchive(arc, DOWNLOAD_DIR, INSTALL_DIR)
        update_receipt(arc, receipt)

    # Decompress the Authoring files.. these are required
    print("Installing authoring support to {}".format(support_files))
    for arc in [f for f in bundle_data['files'] if f['name'] in ARCHIVES_AUTHORING]:
        unarchive(arc, DOWNLOAD_DIR, support_files)
        update_receipt(arc, receipt)

    # Write the install data
    data_dir = args.INSTALL_PREFIX + '/Applications/Audiokinetic/Data'

    print("Writing install data to {}".format(data_dir))
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)
    with open(data_dir + '/' + 'install-table.json', 'w') as out:
        out.write(json.dumps(install_table))

    # And the bundle data
    with open(INSTALL_DIR + '/' + 'bundle-data.json', 'w') as out:
        out.write(json.dumps(bundle_data))

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


def update_receipt(source, receipt):
    """ Add any groups associated with `source` to `receipt` 
        only if they are not already present in `receipt`
    """
    receipt['installed']['files'].append(source['name'])
    for grp in source['groups']:
        newgrp = {'id': grp['groupId'], 'valueId': grp['groupValueId']}
        # Is the group already in the list?
        matches = [item for item in receipt['installed']['groups']
                   if cmp(item, newgrp) == 0]
        if not matches or matches == []:
            receipt['installed']['groups'].append(newgrp)


def decode_payload(payload):
    parsed = json.loads(payload)
    decoded = b64decode(parsed.get('payload', None))
    return json.loads(decoded)


def unarchive(source, download_dir, dest):
    path = download_dir + '/' + source['name']
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
