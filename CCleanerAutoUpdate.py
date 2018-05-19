# -*- coding: UTF-8 -*-
from __future__ import print_function, unicode_literals
import sys
import os
import subprocess
import re
from io import open
import requests

PY3 = sys.version_info >= (3, 0)


def get_html(url):
    res = requests.get(url)
    if not res.ok:
        raise Exception('open url error: {}'.format(url))
    return res.text


# Version String Class
class Version:
    def __init__(self, major=None, minor=None, build=None):
        self.major = major
        self.minor = minor
        self.build = build

    # local version string
    def from_local_version_string(self, version_str):
        vers = version_str.split('.')
        self.major = int(vers[0])
        self.minor = int(vers[1])
        # verse[2] is currently not used (always remained as zero)
        # self.minor = int('%s%s' % (vers[1], vers[2]))
        self.build = int(vers[3])

    # remote version string
    def from_current_version_string(self, version_str):
        vers = version_str.split('.')
        self.major = int(vers[0])
        self.minor = int(vers[1])
        self.build = int(vers[2])

    def __str__(self):
        return '%d/%d/%d' % (self.major, self.minor, self.build)

    # compare (always local <= remote, only need to define !=, ==)
    def __eq__(self, other):
        return isinstance(other, self.__class__) \
               and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


def check_update(config):
    installed = False

    # check CCleaner.exe exists!
    if not os.path.exists(config['ccleaner_path']):
        print('%s does not exist!' % config['ccleaner_path'], file=sys.stderr)
    else:
        installed = True

    iv_txt = None
    if installed:
        # local ccleaner version
        print("Checking installed CCleaner's version...")
        command = 'wmic DATAFILE WHERE NAME="%s" GET version > version.txt' % \
                  config['ccleaner_path']
        subprocess.call(command, shell=True)

        # get version
        with open('version.txt', 'r', encoding="utf-16") as f:
            text = f.read()
            iv_txt = text.split(u'\n')[1].strip()

    # current release version
    print('Checking current CCleaner version at Piriform...')
    release_html = get_html(config['release_url'])
    release_exp = re.compile(config['release_re'],
                             flags=re.UNICODE | re.DOTALL | re.MULTILINE)
    release_srch = release_exp.search(release_html).groups()

    ver_str = release_srch[0].strip()[1:]  # exclude heading 'v'
    release_date = release_srch[1].strip()

    # To canonical version expression.
    installed_ver = Version() if installed else Version(0, 0, 0)
    current_ver = Version()

    if installed:
        installed_ver.from_local_version_string(iv_txt)
    current_ver.from_current_version_string(ver_str)

    print('Installed CCleaner version:', installed_ver)
    print('Current CCleaner version:', current_ver, release_date)

    # compare two
    if installed_ver == current_ver:
        print('You are using current version. Nothing to do.')
        return 0
    else:
        print('New version is available!')

    # installer pre-delete
    if config['keep_file'] == 'pre':
        delete_installer()

    # download current release
    download_html = get_html(config['download_url'])
    download_exp = re.compile(config['download_re'])
    download_src = download_exp.search(download_html)

    url = download_src.groups()[0]
    filename = url.split('/')[-1]

    print('Begin download...')
    res = requests.get(url, stream=True)

    with open(filename, 'wb') as f:
        chunk_read(f, res, report_hook=chunk_report)

    print('Download complete!')

    cmd = filename + ' ' + config['install_arg']

    print('Installing...')

    if subprocess.call(cmd, shell=True) == 0:
        print('Complete!')
    else:
        print('Something went wrong')

    # installer post-delete
    if config['keep_file'] == 'post':
        delete_installer()

    return 0


def chunk_report(bytes_so_far, total_size):
    bar_len = 32
    progress = float(bytes_so_far) / total_size
    filled_len = int(round(bar_len * progress))
    percent = round(progress * 100, 2)

    bar = '█' * filled_len + ' ' * (bar_len - filled_len)
    sys.stdout.write('Downloading |%s| %0.2f%% (%d/%d)\r' % (
    bar, percent, bytes_so_far, total_size))
    sys.stdout.flush()

    if bytes_so_far >= total_size:
        sys.stdout.write('\n')


def chunk_read(f, response, chunk_size=8192, report_hook=None):
    total_size = response.headers['Content-Length'].strip()
    total_size = int(total_size)
    bytes_so_far = 0

    for chunk in response.iter_content(chunk_size):
        f.write(chunk)
        bytes_so_far += len(chunk)

        if report_hook:
            report_hook(bytes_so_far, total_size)

    return bytes_so_far


def parse_config(configfile):
    config = {}
    with open(configfile, 'r') as f:
        for l in f:
            colon = l.find(':')
            prop = l[0:colon].strip()
            val = l[colon + 1:].strip()

            config[prop] = val

    return config


def delete_installer():
    subprocess.call('del ccsetup*.exe', shell=True)
    print('Installer Cleaned!')
    return 0


def main(argv):
    # parse config file
    configfile = './config.cfg'
    if len(argv) == 2:
        configfile = argv[1]
    config = parse_config(configfile)

    # begin the job
    return check_update(config)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
