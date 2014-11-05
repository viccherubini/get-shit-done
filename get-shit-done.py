#!/usr/bin/env python

import sys
import getpass
import subprocess
import os
import json

def exit_error(error):
    print >> sys.stderr, error
    exit(1)

iniFile = os.path.expanduser(os.path.join("~", ".get-shit-done.ini"))
restartNetworkingCommand = ["/etc/init.d/networking", "restart"]
hostsFile = '/etc/hosts'
startToken = '## start-gsd'
endToken = '## end-gsd'
siteList = ['reddit.com', 'forums.somethingawful.com', 'somethingawful.com',
            'digg.com', 'break.com', 'news.ycombinator.com', 'infoq.com',
            'bebo.com', 'twitter.com', '', 'blip.com',
            'youtube.com', 'vimeo.com', 'delicious.com', 'flickr.com',
            'friendster.com', 'hi5.com', 'linkedin.com', 'livejournal.com',
            'meetup.com', 'myspace.com', 'plurk.com', 'stickam.com',
            'stumbleupon.com', 'yelp.com', 'slashdot.com','thedailywtf.com',
	    'facebook.com','okcupid.com','craigslist.org','hasgeek.com',
            'questionablecontent.net', 'xkcd.com', 'smbc-comics.com','oglaf.com',
            'limbero.org','existentialcomics.com', 'zenpencils.com','phdcomics.com',
            ]


if os.path.exists(iniFile):
	iniF = open(iniFile)
	try:
		iniF_in = iniF.read()
                print iniF_in
		iniF_out = json.loads(iniF_in)
		if iniF_out.has_key ("sites"):
			siteList = siteList + iniF_out.get("sites")
		elif iniF_out.has_key ("siteList"):
			siteList =  iniF_out.get("siteList")
	finally:
		iniF.close()

def rehash():
    subprocess.check_call(restartNetworkingCommand)

def work():
    hFile = open(hostsFile, 'a+')
    contents = hFile.read()

    if startToken in contents and endToken in contents:
        exit_error("Work mode already set.")

    print >> hFile, startToken

    for site in siteList:
        print >> hFile, "127.0.0.10\t" + site
        print >> hFile, "127.0.0.10\twww." + site
    print >> hFile, endToken

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
    try:
	{"work": work, "play": play}[sys.argv[1]]()
    except Exception,e:
	print e


if __name__ == '__main__':
	main()
