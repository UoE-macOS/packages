#!/usr/bin/python
from __future__ import print_function
import urllib2
import sys
import os
import json
import shutil
import subprocess
import argparse
from distutils.version import LooseVersion
import xml.etree.ElementTree as ET

VERSION = '0.0.1'
DESCRIPTION = 'TBD'

def process_args(argv=None):
    """Process any commandline arguments"""
    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     version=VERSION)

    parser.add_argument('--download-dir',
                        dest='DOWNLOAD_DIR', default='./_downloads', 
                        help=('Directory in which to download the installers.'
                              'Installers will be deleted when finished, unless '
                              '--preserve-downloads is specified '
                              'Default: ./_downloads'))

    parser.add_argument('--preserve-downloads', default=False, action='store_true',
                        dest='PRESERVE', help=('Do not delete downloads after installation. '
                                               'WARNING: requires at least 130GB of free space ' 
                                               'in the download directory, PLUS the same again on '
                                               'the installation target.'))

    parser.add_argument('--download-only', default=False, action='store_true',
                        dest='DOWNLOAD_ONLY', 
                        help=('Do not install, only download (implies --preserve-downloads)'))

    parser.add_argument('--updates-only', default=False, action='store_true',
                        dest='UPDATES_ONLY', 
                        help=('Do not look for new fullproduct installers, only updates. This '
                              'can hopefully be used to update an existing installation. YMMV'))

    args = parser.parse_args(argv)

    if args.DOWNLOAD_ONLY:
        args.PRESERVE = True

    return args

INSTALL_RECEIPTS = '/var/db/NativeInstrumentsReceipts.txt'

BASEURL = 'https://api.native-instruments.com/'

NATIVE_ACCESS_URL = 'https://www.native-instruments.com/fileadmin/downloads/Native_Access_Installer.dmg'

PROTOBUF_HEADERS = {'Accept': 'application/x-protobuf',
                    'Content-Type': 'application/x-protobuf'}

JSON_HEADERS = {'Accept': 'application/json',
                'Content-Type': 'application/x-protobuf'}

METALINK_HEADERS = {'Accept': 'application/metalink4+xml'}

USER_AGENT = {'User-Agent': 'NativeAccess/1.7.2 (R88)'}

KOMPLETE_11_PRODUCTS = ["00b224af-b357-4dfe-9929-414bbdf97d6f",
                        "02cf2683-8802-4ccc-b7c4-78c89f7d3fad",
                        "07c2ce64-1477-405c-a6da-eec6d4283afa",
                        "2665347d-14a1-4fbd-896b-961c554adc9a",
                        "27522c8a-4430-4369-969e-a944757ece34",
                        "27cf9287-ad1e-4877-9ca9-43a143069290",
                        "36e6e129-e11a-4262-b2d0-42e1e436c518",
                        "391e5d29-7d61-4ee6-a182-0ea4848f347f",
                        "39232cc5-01ba-4404-b5aa-00af0c82b92e",
                        "3cede7e3-b10d-4c72-a6cb-fe5217399507",
                        "41c9f7cf-0a44-4459-8291-5ba86ffef5fd",
                        "45711249-0863-47d4-a951-7df3c09c107f",
                        "45b33149-83fb-4ed0-b716-fa3cb49ed0c2",
                        "4a602cbe-9e7e-43e5-957c-50e85acf0b6d",
                        "4c87b5ed-5b02-4a1e-aab9-ecfe505b8ab6",
                        "52c1cbc7-e22c-4dd8-b310-700de064999a",
                        "5c7426db-e6cb-4074-aba6-22ebf03934a1",
                        "618d261a-6459-4189-8dcf-bace3b0a364c",
                        "6276d356-7151-490f-822c-6fbf497e4a17",
                        "65a280f7-c9b3-4ae2-b9ce-b945cfa4dcae",
                        "68cffbb8-7b20-4e9a-bee5-1dab962049ff",
                        "709661c3-0f2e-432e-a22c-2ece8af86b68",
                        "7aea8f0e-b5be-4394-8f23-8d04091890e8",
                        "7fa92dc1-2eb7-439f-9c3e-66af0ef70c3b",
                        "84111eb8-03eb-4afc-8da4-425cb1a7d310",
                        "87151caa-811c-436b-84b5-c7d0510d4aca",
                        "8f244475-49f2-4548-93a4-f8e24539901d",
                        "904ce876-6b5c-45de-b3f5-79c1ce2793d6",
                        "9181966c-399d-4028-af70-51b9b3626e44",
                        "9a53fb08-ac38-4757-9eef-f017b9797618",
                        "9b71b5fd-1c06-412a-9f17-83be07c1ea35",
                        "9f7e5f3c-dee3-45aa-88ec-005e0f441a56",
                        "a0ebfb22-988b-40d8-b050-27b40c5ab653",
                        "a379f93a-d657-471a-9539-24c093bdd5e1",
                        "b43b661c-8d44-40a5-a6fe-8c1cab8c2089",
                        "b4c9758d-87b0-4c3a-9062-eadd03df8857",
                        "b6668dfe-ccfa-43a1-b3fa-dd8bf0dbbcfd",
                        "c6b8ce64-9c20-49bb-96a7-4a13e3b2edfd",
                        "cbb449a1-5808-4675-ba14-3439ad235eab",
                        "cf11c1f6-1d76-432f-aece-52ef5305a14d",
                        "d61654f3-8059-43dd-91c3-424cda8fbabc",
                        "dd548265-9323-4a49-b4fa-0cf43b2d9647",
                        "df57aef4-9e82-4e78-b46c-dfb2a1f03a37",
                        "e21acc84-ce2e-4601-b820-add29eeb56a8",
                        "e2398f2f-ce52-4c7e-aa58-f76b9668cf42",
                        "e39d9afa-4457-43a5-bc1e-f6e87426075b",
                        "e612c6f8-d7ea-428c-ab30-6059c7797d16",
                        "ebd03fa6-bb2d-4275-bfb7-778c24d712b2",
                        "ecea4995-a1db-4eb8-a731-1c783df1ba91",
                        "f1131a56-9fc2-4ec3-a042-1e3eae7d6661",
                        "f1e4c3f3-300a-413f-983e-cb8fb758397e",
                        "f2ce397b-a6f5-4680-90a2-2b567517fa61",
                        "f46d59cb-cbcf-444d-9832-67bf22608c73",
                        "fb4b8d73-b9b1-46d3-add1-9cda22f83dc1"]

AUTH_HEADER = {'Authorization': ''}


def main(args):
    global AUTH_HEADER

    dist_types = ['updates']
    if not args.UPDATES_ONLY:
        dist_types.insert(0, 'full-products')

    # Install the latest version of Native Access
    install_native_access(args.DOWNLOAD_DIR)

    # This authentication token is embedded in the application. 
    # Make sure we have an up-to-date copy.   
    token = get_bearer_token('/Applications/Native Access.app/Contents/MacOS/Native Access')

    # Stash our auth token.
    AUTH_HEADER['Authorization'] = 'Bearer ' + token

    check_create_download_dirs(args.DOWNLOAD_DIR, dist_types)

    for prod in KOMPLETE_11_PRODUCTS:
        for dist_type in dist_types:
            try:
                artifacts = get_artifacts(prod, dist_type)

                latest = get_latest_artifacts(artifacts)

                for art in latest:
                    files = process_artifact(art, download=dist_type)
                    if not files: 
                        # This artifact has nothing for us to install
                        continue
                    for (candidate, version) in files:
                        if is_installed(candidate, version) or args.DOWNLOAD_ONLY:
                            # Alreday installed, or user has requested no installation
                            continue
                        path = None # Set this to something so we can reference it in the finally block
                        try:
                            path, pkg = attach_image(candidate)
                            install_pkg(path + '/' + pkg, candidate, version)
                            if not args.PRESERVE:
                                os.unlink(candidate)
                        except subprocess.CalledProcessError as err:
                            print("INSTALL FAILED: {} ({})".format(pkg, err))
                            continue
                        finally:
                            if path:
                                unmount(path)
            except urllib2.HTTPError as err:
                sys.stderr.write("{}\n".format(err))
                continue


def check_create_download_dirs(d_dir, dist_types):
    for atype in dist_types:
        if not os.path.isdir(d_dir + '/' + atype):
            os.makedirs(d_dir + '/' + atype)


def get_bearer_token(path):
    strings = subprocess.check_output(['strings', path]).split('\n')
    token = [s for s in strings if s.startswith('eyJhbGciOiJSUzI1NiI')]
    return token[0]


def install_native_access(downloads):
    print('Downloading Natve Access...')
    fetch(NATIVE_ACCESS_URL, dest=downloads + '/native-access.dmg')
    path, pkgs = attach_image(downloads + '/native-access.dmg')
    dest = '/Applications/Native Access.app'
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    print('Installing Native Access...')
    shutil.copytree(path + '/' + 'Native Access.app', '/Applications/Native Access.app')
    unmount(path)



def is_installed(target_file, version):
    receipts = INSTALL_RECEIPTS
    ident = '{}-{}'.format(os.path.basename(target_file), version)
    if not os.path.isfile(receipts):
        print("{} is not installed".format(ident))
        return False
    else:
        with open(receipts, 'r') as rcpt:
            result = ident in rcpt.read().split('\n')
        if result:
            print("{} is installed already".format(ident))
        else:
            print("{} is not installed".format(ident))
        return result


def attach_image(img):
    if not os.path.isfile(img) or not img.endswith(('.iso', '.dmg')):
        return None

    output = subprocess.check_output(['hdiutil', 'attach', img])
    mounted_path = output.split("\t")[-1].strip()
    pkgs = [a for a in os.listdir(mounted_path) if a.endswith('.pkg')]
    try:
        pkgs = pkgs[0]
    except IndexError: # There may not be any packages...
        pkgs = None
    return (mounted_path, pkgs)


def unmount(path):
    subprocess.check_call(['hdiutil', 'detach', path])


def install_pkg(package, from_file, version):
    # Will raise a subprocess.CalledProcessError in case of failure
    print("Installing: ", package)
    receipts = INSTALL_RECEIPTS
    ident = '{}-{}'.format(os.path.basename(from_file), version)
    cmd = ['/usr/sbin/installer', '-pkg', package, '-target', '/']
    subprocess.check_call(cmd)
    with open(receipts, 'a+') as rcpt:
        rcpt.write('{}\n'.format(ident))


def process_artifact(artifact, download=False):
    # No Windows, thanks.
    if not artifact['platform'] in ['mac_platform', 'all_platform']:
        return None

    print("{}, {}".format(artifact['title'], artifact['version']))

    files_to_return = []
    for afile in artifact['files']:

        # We don't want 'downloader_type' files - just ISOs, updaters and installers
        if not afile['type'] in ['iso_type', 'update_type', 'installer_type']:
            continue

        url = get_download_url(afile)
        print('{}, {}M, {}'.format(
            afile['target_file'], afile['filesize']/1024/1024, url))
        
        if download and not is_installed(afile['target_file'], artifact['version']):
            outfile = '_downloads/' + download + '/' + afile['target_file']
            if os.path.isfile(outfile) and not afile['filesize'] > os.path.getsize(outfile):
                files_to_return.append((outfile, artifact['version']))
                continue

            print("Downloading: ", afile['target_file'])
            fetch(url, headers=PROTOBUF_HEADERS, dest=outfile)
            files_to_return.append((outfile, artifact['version']))

    return files_to_return

        
def get_download_url(a_file):
    # The 'url' attribute of a_file leads to an XML metalink
    # document which contains various information about the download
    # including the the actual download URL we need.
    meta_url = BASEURL + '/v1/download/' + a_file['url']
    resp = fetch(meta_url, headers=METALINK_HEADERS)
    tree = ET.fromstring(resp.read())
    url = tree.findall('.//{urn:ietf:params:xml:ns:metalink}url')[0].text
    return url


def get_artifacts(prod, dist_type):
    if dist_type not in ['full-products', 'updates']:
        return None
    url = BASEURL + '/v1/download/' + dist_type + '/' + prod
    resp = fetch(url, headers=JSON_HEADERS)
    resp_data = json.loads(resp.read())['response_body']
    return resp_data['artifacts']


def get_latest_artifacts(artifacts):
    sorted_versions = sorted(
        artifacts, key=lambda k: LooseVersion(k['version']))
    latest_version_string = sorted_versions[-1]['version']
    latest = [v for v in sorted_versions if v['version']
              == latest_version_string]
    return latest


def fetch(url, dest=None, data=None, headers=None):
    """ Fetch `url`.
        If `data` is present send a POST request, otherwise GET
        If `dest` is present, store the result there, otherwise
        return a file-like object.
    """
    myheaders = {}
    myheaders.update(USER_AGENT)
    myheaders.update(AUTH_HEADER)

    if headers is not None:
        myheaders.update(headers)

    # sys.stderr.write("fetch: {}\n".format(url))
    if data:
        # If data is serialisable, send it as json
        try:
            mydata = json.dumps(data)
        except:
            # Just send whatever we were passed, raw
            mydata = data
        req = urllib2.Request(url, headers=myheaders, data=mydata)
        resp = urllib2.urlopen(req)
    else:
        req = urllib2.Request(url, headers=myheaders)
        resp = urllib2.urlopen(req)
    if dest:
        with open(dest, 'wb') as fp:
            shutil.copyfileobj(resp, fp)
    else:
        return resp


if __name__ == '__main__':
    main(process_args())
