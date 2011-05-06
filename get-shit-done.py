#!/usr/bin/env python

import sys
import getpass
import subprocess
import os
from os import path
from __future__ import print_function

def exit_error(error):
    print(error, file=sys.stderr)
    exit(1)
    
iniFile = path.expanduser(path.join("~", ".get-shit-done.ini"))
restartNetworkingCommand = ["/etc/init.d/networking", "restart"]
hostsFile = '/etc/hosts'
startToken = '## start-gsd'
endToken = '## end-gsd'
siteList = ['reddit.com', 'forums.somethingawful.com', 'somethingawful.com',
            'digg.com', 'break.com', 'news.ycombinator.com', 'infoq.com',
            'bebo.com', 'twitter.com', 'facebook.com', 'blip.com',
            'youtube.com', 'vimeo.com', 'delicious.com', 'flickr.com',
            'friendster.com', 'hi5.com', 'linkedin.com', 'livejournal.com',
            'meetup.com', 'myspace.com', 'plurk.com', 'stickam.com',
            'stumbleupon.com', 'yelp.com', 'slashdot.com']

if os.path.exists(iniFile):
    iniF = open(iniFile)
    try:
        for line in iniF:
            key, value = [each.strip() for each in line.split("=", 1)]
            if key == "sites":
                siteList = [value]
            elif key == "sites[]":
                siteList.append(value)
    finally:
        iniF.close()

def rehash():
    subprocess.check_call(restartNetworkingCommand)

def work():
    hFile = open(hostsFile, 'a+')
    contents = hFile.read()

    if startToken in contents and endToken in contents:
        exit_error("Work mode already set.")

    print(startToken, file=hFile)

    for site in siteList:
        print("127.0.0.1\t" + site, file=hFile)
        print("127.0.0.1\twww." + site, file=hFile)

    print(endToken, file=hFile)

    rehash()

def play():
    hFile = open(hostsFile, "r+")
    lines = hFile.readlines()

    startIndex = -1

    for index, line in enumerate(lines):
        if line.strip() == startToken:
            startIndex = index

    if startIndex > -1:
        lines = lines[0:startIndex]

        hFile.seek(0)
        hFile.write(''.join(lines))
        hFile.truncate()

        rehash()

def main():
    if getpass.getuser() != 'root':
        exit_error('Please run script as root.')
    if len(sys.argv) != 2:
        exit_error('usage: ' + sys.argv[0] + ' [work|play]')
    {"work": work, "play": play}[sys.argv[1]]()
