#!/usr/bin/env python

import sys
import getpass
import subprocess
import os

def exitWithError(error):

	print >> sys.stderr, error
	exit(1)

if (len(sys.argv) == 1):
	exitWithError('usage: ' + sys.argv[0] + ' [work|play]')
	
if (getpass.getuser() != 'root'):
	exitWithError('Please run script as root.')
	
homedir = os.getenv('HOME')
iniFile = homedir + "/.get-shit-done.ini"

siteList = []

if os.path.exists(iniFile):

	iniF = open(iniFile)
	
	for line in iniF:
	
		parts = line.split("=")
		
		if parts[0].strip() == "sites[]":
			siteList.append(parts[1].strip())

else:	

	siteList = ['reddit.com', 'forums.somethingawful.com', 'somethingawful.com',
		'digg.com', 'break.com', 'news.ycombinator.com',
		'infoq.com', 'bebo.com', 'twitter.com',
		'facebook.com', 'blip.com', 'youtube.com',
		'vimeo.com', 'delicious.com', 'flickr.com',
		'friendster.com', 'hi5.com', 'linkedin.com',
		'livejournal.com', 'meetup.com', 'myspace.com',
		'plurk.com', 'stickam.com', 'stumbleupon.com',
		'yelp.com', 'slashdot.com']
	
restartNetworkingCommand = ["/etc/init.d/networking", "restart"]
hostsFile = '/etc/hosts'
startToken = '## start-gsd'
endToken = '## end-gsd'

action = sys.argv[1]

if action == 'work':

	hFile = open(hostsFile, 'a+')
	contents = hFile.read()
	
	if (startToken in contents and endToken in contents):
		exitWithError("Work mode already set.")
		
	print >> hFile, startToken
	
	for site in siteList:
	
		print >> hFile, "127.0.0.1\t" + site
		print >> hFile, "127.0.0.1\twww." + site
		
	print >> hFile, endToken
	
	subprocess.call(restartNetworkingCommand)
	
elif action == 'play':

	hFile = open(hostsFile, "r+")
	lines = hFile.readlines()
	
	startIndex = -1
	
	for index, line in enumerate(lines):
		if (line.strip() == startToken):
			startIndex = index
			
	if (startIndex > -1):
		
		lines = lines[0:startIndex]
		
		hFile.seek(0)
		hFile.write(''.join(lines))
		hFile.truncate()
				
		subprocess.call(restartNetworkingCommand)
