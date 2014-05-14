#!/usr/bin/python
# Filename : timer.py

import get_shit_done
import sys
import time
import threading
import re

if __name__ == '__main__':
	
	working_time = 0.0
	times = {'h' : 0.0, 'm' : 0.0 , 's' : 0.0}
	pattern1 = re.compile('(h|m|s)=[0-9]+\.?[0-9]*')
	pattern2 = re.compile('[0-9]+\.?[0-9]*')
	if len(sys.argv) > 1:
		for i, arg in enumerate(sys.argv):
			if i > 0:
				if pattern1.match(arg):
					d = arg.split('=')
					times[d[0]] = times[d[0]] + float(d[1])
				elif pattern2.match(arg):
					times['s'] = times['s'] + float(arg)
	
	working_time = (times['h'] * 3600) + (times['m'] * 60) + times['s']
	
	get_shit_done.work()
	time.sleep(working_time)
	get_shit_done.play()
