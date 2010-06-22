#!/usr/bin/php
<?php

if ( 1 == $argc ) {
	exitWithError("Usage: get-shit-done <work|play>");
}

$whoami = `whoami`;
$whoami = trim(strtolower($whoami));

if ( 'root' != strtolower($whoami) ) {
	exitWithError("Please run script as root.");
}

$siteList = array(
	'reddit.com', 'forums.somethingawful.com', 'somethingawful.com',
	'digg.com', 'break.com', 'news.ycombinator.com',
	'infoq.com', 'bebo.com', 'twitter.com',
	'facebook.com', 'blip.com', 'youtube.com',
	'vimeo.com', 'delicious.com', 'flickr.com',
	'friendster.com', 'hi5.com', 'linkedin.com',
	'livejournal.com', 'meetup.com', 'myspace.com',
	'plurk.com', 'stickam.com', 'stumbleupon.com',
	'yelp.com'
);

$hostsFile = '/etc/hosts';
$startToken = '## start-gsd';
$endToken = '## end-gsd';

$action = $argv[1];

switch ( $action ) {
	case 'work': {
		$fh = fopen($hostsFile, 'a');
		if ( false === $fh ) {
			exitWithError("Failed to open the hosts file.");
		}
		
		fwrite($fh, $startToken . PHP_EOL);
		foreach ( $siteList as $site ) {
			fwrite($fh, "127.0.0.1\t{$site}" . PHP_EOL);
		}
		fwrite($fh, $endToken . PHP_EOL);
		
		fclose($fh);
		
		`/etc/init.d/networking restart`;
		
		break;
	}
	
	
	case 'play': {
		$hostContents = file($hostsFile);
		if ( false === $hostContents ) {
			exitWithError("Failed to open the hosts file.");
		}
		
		$startIndex = -1;
		for ( $i=0; $i<count($hostContents); $i++ ) {
			if ( trim($hostContents[$i]) == $startToken ) {
				$startIndex = $i;
			}
		}
		
		$hostContents = array_slice($hostContents, 0, $startIndex);
		
		file_put_contents($hostsFile, $hostContents);
		
		`/etc/init.d/networking restart`;
		
		break;
	}
}

function exitWithError($error) {
	echo $error;
	echo PHP_EOL;
	exit(1);
}