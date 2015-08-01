# -*- coding: UTF-8 -*-
import sys
import os
import urllib2
import re


def GetHTML(URL):
    res = urllib2.urlopen(URL)
    html = res.read()
    res.close()
    return html


# Version String Class
class Version:
    major = None
    minor = None
    build = None

    # local version string
    def FromLocalVersionString(self, localVersionString):
        vers = localVersionString.split('.')
        self.major = int(vers[0])
        self.minor = int(vers[1])
        # self.minor = int('%s%s' % (vers[1], vers[2]))  #verse[2] is currently not used (always remained as zero)
        self.build = int(vers[3])

    # remote version string
    def FromCurrentVersionString(self, currentVersionString):
        vers = currentVersionString.split('.')
        self.major = int(vers[0])
        self.minor = int(vers[1])
        self.build = int(vers[2])

    def __str__(self):
        return '%d/%d/%d' % (self.major, self.minor, self.build)

    # compare (be aware that always local <= remote, only need to define !=, ==)
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


def CheckUpdate(config):
    # check CCleaner.exe exists!
    if os.path.exists(config['ccleaner_path']) == False:
        print >> sys.stderr, '%s does not exist!' % config['ccleaner_path']
        return 1

    # local ccleaner version
    print "Checking installed CCleaner's version..."
    command = 'wmic DATAFILE WHERE NAME="%s" GET version > version.txt' % config['ccleaner_path']
    os.system(command)

    # get version
    with open('version.txt', 'r') as f:
        text = unicode(f.read(), 'utf-16')
        iv_txt = text.split(u'\n')[1].strip()

    # current release version
    print 'Checking current CCleaner version at Piriform...'
    release_html = GetHTML(config['release_url'])
    release_exp = re.compile(config['release_re'], re.DOTALL | re.MULTILINE)
    release_srch = release_exp.search(release_html).groups()

    cv_txt = release_srch[0].strip()[1:]  # exclude heading 'v'
    reldate = release_srch[1].strip()

    # To canonical versino expression.
    installed_ver = Version()
    current_ver = Version()

    installed_ver.FromLocalVersionString(iv_txt)
    current_ver.FromCurrentVersionString(cv_txt)

    print 'Installed CCleaner version:', installed_ver
    print 'Current CCleaner version:', current_ver, reldate

    # compare two
    if installed_ver == current_ver:
        print 'You\'re using current version. Nothing to do.'
        return 0
    else:
        print 'There\'s a new update available!'

    # installer pre-delete
    if config['keep_file'] == 'pre':
        DeleteInstaller()

    # download current release
    download_html = GetHTML(config['download_url'])
    download_exp = re.compile(config['download_re'])
    download_srch = download_exp.search(download_html)

    url = download_srch.groups()[0]
    filename = url.split('/')[-1]

    print 'Begin download...'
    obj = urllib2.urlopen(url)

    with open(filename, 'wb') as f:
        chunk_read(f, obj, report_hook=chunk_report)

    print 'Download complete!'

    cmd = filename + ' ' + config['install_arg']

    print 'Installing...'
    os.system(cmd)
    print 'Complete!'

    # installer post-delete
    if config['keep_file'] == 'post':
        DeleteInstaller()

    return 0


def chunk_report(bytes_so_far, chunk_size, total_size):
    percent = float(bytes_so_far) / total_size
    percent = round(percent * 100, 2)
    sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" %
                     (bytes_so_far, total_size, percent))

    if bytes_so_far >= total_size:
        sys.stdout.write('\n')


def chunk_read(f, response, chunk_size=8192, report_hook=None):
    total_size = response.info().getheader('Content-Length').strip()
    total_size = int(total_size)
    bytes_so_far = 0

    while 1:
        chunk = response.read(chunk_size)
        f.write(chunk)
        bytes_so_far += len(chunk)

        if not chunk:
            break

        if report_hook:
            report_hook(bytes_so_far, chunk_size, total_size)

    f.close()

    return bytes_so_far


def ParseConfig(configfile):
    config = {}
    with open(configfile, 'r') as f:
        for l in f:
            colon = l.find(':')
            prop = l[0:colon].strip()
            val = l[colon + 1:].strip()

            config[prop] = val

    return config


def DeleteInstaller():
    os.system('del ccsetup*.exe')
    print 'Installer Cleaned!'
    return 0


def main(argv):
    # parse config file
    configfile = './config.cfg'
    if len(argv) == 2:
        configfile = argv[1]
    config = ParseConfig(configfile)

    # begin the job
    return CheckUpdate(config)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
