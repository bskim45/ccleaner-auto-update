# -*- coding: UTF-8 -*-
from __future__ import print_function, unicode_literals
import sys
import os
import subprocess
import re
from io import open
import requests
import win_unicode_console

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

    @classmethod
    def from_local_version_string(cls, version_str):
        # type: (str) -> Version
        """
        parse local version string
        """
        vers = version_str.split('.')

        return Version(
            major=int(vers[0]),
            minor=int(vers[1]),
            # verse[2] is currently not used (always remained as zero)
            # self.minor = int('%s%s' % (vers[1], vers[2]))
            build=int(vers[3])
        )

    @classmethod
    def from_current_version_string(cls, version_str):
        # type: (str) -> Version
        """
        parse remote version string
        """
        vers = version_str.split('.')

        return Version(
            major=int(vers[0]),
            minor=int(vers[1]),
            build=int(vers[2])
        )

    def __str__(self):
        return '%d/%d/%d' % (self.major, self.minor, self.build)

    # compare (always local <= remote, only need to define !=, ==)
    def __eq__(self, other):
        return isinstance(other, self.__class__) \
               and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


def get_installed_version(exe_path):
    # type: (str) -> Version
    # local ccleaner version
    command = 'wmic DATAFILE WHERE NAME="{}" GET version > version.txt'.format(
        exe_path)
    subprocess.call(command, shell=True)

    # get version
    iv_txt = None
    with open('version.txt', 'r', encoding="utf-16") as f:
        text = f.read()
        iv_txt = text.split('\n')[1].strip()

    return (
        Version.from_local_version_string(iv_txt) if iv_txt
        else Version(0, 0, 0)
    )


def get_release_version(check_url, regx_str):
    # type: (str, str) -> (Version, str)
    release_html = get_html(check_url)
    release_exp = re.compile(
        regx_str, flags=re.UNICODE | re.DOTALL | re.MULTILINE)
    release_str = release_exp.search(release_html).groups()

    ver_str = release_str[0].strip()[1:]  # exclude heading 'v'
    release_date = release_str[1].strip()

    return Version.from_current_version_string(ver_str), release_date


def check_update(config):
    installed = False

    # check CCleaner.exe exists!
    if not os.path.exists(config['ccleaner_path']):
        print('%s does not exist!' % config['ccleaner_path'], file=sys.stderr)
    else:
        installed = True

    print("Checking installed CCleaner's version...")
    installed_ver = get_installed_version(
        config['ccleaner_path']) if installed else Version(0, 0, 0)

    print('Checking current CCleaner version at Piriform...')
    current_ver, release_date = get_release_version(
        config['release_url'], config['release_re'])

    print('Installed CCleaner version:',
          installed_ver if installed else 'Not installed')
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

    win_unicode_console.enable()
    result = check_update(config)
    win_unicode_console.disable()

    return result


if __name__ == '__main__':
    sys.exit(main(sys.argv))
