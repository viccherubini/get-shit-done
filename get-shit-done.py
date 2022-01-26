#!/usr/bin/env python

from __future__ import print_function
import sys
import getpass
import subprocess
import os
import json

ini_local = os.path.expanduser(os.path.join("~", ".config/get-shit-done.ini"))
ini_global = './sites.ini'
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
            'limbero.org', 'plus.google.com', 'moneycontrol.com', 'quora.com',
            'primevideo.com', 'netflix.com', 'dotabuff.com', 'instagram.com',
            ]


def exit_error(error):
    print(error, file=sys.stderr)
    exit(1)


if "linux" in sys.platform:
    restart_network_command = ["/etc/init.d/networking", "restart"]
elif "darwin" in sys.platform:
    restart_network_command = ["dscacheutil", "-flushcache"]
elif "win32" in sys.platform:
    restart_network_command = ["ipconfig", "/flushdns"]
else:
    # Intention isn't to exit, as it still works, but just requires some
    # intervention on the user's part.
    message = '"Please contribute DNS cache flush command on GitHub."'
    restart_network_command = ['echo', message]

def ini_to_array(ini_file):
    # this enables the ini file to be written like
    # sites = google.com, facebook.com, quora.com ....
    if os.path.exists(ini_file):
        f = open(ini_file)
        sites = []
        for line in f:
            key, value = [each.strip() for each in line.partition("=")[::2]]
            if key == "sites":
                for item in [each.strip() for each in value.split(",")]:
                    sites.append(item)
        return sites
    else:
      return []

hosts_file = '/etc/hosts'

if "win32" in sys.platform:
    hosts_file = '/Windows/System32/drivers/etc/hosts'

start_token = '## start-gsd'
end_token = '## end-gsd'
site_list = ini_to_array(ini_global) + ini_to_array(ini_local)

def rehash():
    subprocess.check_call(restart_network_command)

def work():
    hFile = open(hosts_file, 'a+')
    contents = hFile.read()

    if start_token in contents and end_token in contents:
        exit_error("Work mode already set.")
        hFile.close()

    print(start_token, file=hFile)

    # remove duplicates by converting list to a set
    for site in set(site_list):
        print("127.0.0.1\t" + site, file=hFile)
        print("127.0.0.1\twww." + site, file=hFile)

    print(end_token, file=hFile)

    hFile.close()
    rehash()

def play():
    hosts_file_handle = open(hosts_file, "r+")
    lines = hosts_file_handle.readlines()

    startIndex = -1

    for index, line in enumerate(lines):
        if line.strip() == start_token:
            startIndex = index

    if startIndex > -1:
        lines = lines[0:startIndex]

        hosts_file_handle.seek(0)
        hosts_file_handle.write(''.join(lines))
        hosts_file_handle.truncate()

        rehash()

def main():
    if getpass.getuser() != 'root' and 'win32' not in sys.platform:
        exit_error('Please run script as root.')
    if len(sys.argv) != 2:
        exit_error('usage: ' + sys.argv[0] + ' [work|play]')
    try:
        {"work": work, "play": play}[sys.argv[1]]()
    except KeyError:
        exit_error('usage: ' + sys.argv[0] + ' [work|play]')

if __name__ == "__main__":
    main()
