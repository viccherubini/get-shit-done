#!/usr/bin/env php
<?php

if ( 1 == $argc ) {
  exitWithError("usage: " . $argv[0] . " [work | play]");
}

$whoami = trim(`whoami`);
if ( 'root' != strtolower($whoami) ) {
  exitWithError("Please run script as root.");
}

$homedir = trim(`cd ~ && pwd`);
$iniLocal = $homedir.'/.config/get-shit-done.ini';
$iniGlobal = __DIR__ . '/sites.ini';

$uname = trim(`uname`);

if ( $uname == 'Linux' ) {
    $restartNetworkingCommand = '/etc/init.d/networking restart';
} elseif ( $uname == 'Darwin' ) {
    $restartNetworkingCommand = 'dscacheutil -flushcache';
} else {
    $message = '"Please contribute DNS cache flush command on GitHub."';
    $restartNetworkingCommand = "echo $message";
    # Intention isn't to exit, as it still works, but just requires some
    # intervention on the user's part.
}

$hostsFile = '/etc/hosts';
$startToken = '## start-gsd';
$endToken = '## end-gsd';
$siteList = iniToArray($iniGlobal);

if (file_exists($iniLocal)) {
  $siteList = (array_merge($siteList, iniToArray($iniLocal)));
}

$action = $argv[1];

switch ( $action ) {
  case 'work': {
    $contents = file_get_contents($hostsFile);
    if($contents && strpos($contents, $startToken) !== false && strpos($contents, $endToken) !== false) {
      exitWithError("Work mode already set.");
    }

    $fh = fopen($hostsFile, 'a');
    if ( false === $fh ) {
      exitWithError("Failed to open the hosts file.");
    }

    fwrite($fh, $startToken . PHP_EOL);
    foreach ( $siteList as $site ) {
      fwrite($fh, "127.0.0.1\t{$site}" . PHP_EOL);
      fwrite($fh, "127.0.0.1\twww.{$site}" . PHP_EOL);
    }
    fwrite($fh, $endToken . PHP_EOL);

    fclose($fh);

    shell_exec($restartNetworkingCommand);

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

    if ( $startIndex > -1 ) {
      $hostContents = array_slice($hostContents, 0, $startIndex);
      file_put_contents($hostsFile, $hostContents);
      shell_exec($restartNetworkingCommand);
    }

    break;
  }

  default: {
    exitWithError("usage: " . $argv[0] . " [work | play]");
  }
}

function exitWithError($error) {
  fwrite(STDERR, $error . PHP_EOL);
  exit(1);
}

function iniToArray($iniFile) {
  $iniContents = parse_ini_file($iniFile);

  return array_map('trim', explode(',', $iniContents["sites"]));
}
