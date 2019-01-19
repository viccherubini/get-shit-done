#!/bin/bash

E_NO_PARAMS=1
E_USER_NOT_ROOT=2
E_NO_HOSTS_FILE=3
E_ALREADY_SET=4
E_WEIRD_PARAMS=5

exit_with_error()
{
    # output to stderr
    echo $2 >&2

    print_help

    exit $1
}

trim()
{
    echo $1
}

to_lower()
{
    echo $1 | tr '[A-Z]' '[a-z]'
}

print_help()
{
    cat <<EOF
Usage: `basename $0` [work | play]
EOF
}

# just appends sites lines to the
# end of first param file
work()
{
    # if no hosts file found...
    [ -e "$1" ] || exit_with_error $E_NO_HOSTS_FILE "No hosts file found"

    ini_file="$HOME/.config/get-shit-done.ini"

    site_list=( 'reddit.com' 'forums.somethingawful.com' 'somethingawful.com'
		'digg.com' 'break.com' 'news.ycombinator.com'
		'infoq.com' 'bebo.com' 'twitter.com'
		'facebook.com' 'blip.com' 'youtube.com'
		'vimeo.com' 'delicious.com' 'flickr.com'
		'friendster.com' 'hi5.com' 'linkedin.com'
		'livejournal.com' 'meetup.com' 'myspace.com'
		'plurk.com' 'stickam.com' 'stumbleupon.com'
		'yelp.com' 'slashdot.org' )

    file="$1"

    # check if work mode has been set
    if grep $start_token $file &> /dev/null; then
        if grep $end_token $file &> /dev/null; then
            exit_with_error $E_ALREADY_SET "Work mode already set."
        fi
    fi

    echo $start_token >> $file

    printf '127.0.0.1\t%s\n'     "${site_list[@]}" >> $file
    printf '127.0.0.1\twww.%s\n' "${site_list[@]}" >> $file

    # Append sites from the ini file by parsing in the following manner:
    # * Take only the relevant lines begining with "sites ="
    # * Take the right side of equal sign, remove commas
    # * and split elements on single lines
    # * Print the lines prefixed with localhost and www.
    cat $ini_file \
        | sed '/^\s*sites\s*=/!d' \
        | sed 's/^.*=\(.*\)/\1/g;s/,/\n/g;s/ //g' \
        | sed 's/^/127.0.0.1\t/;p;s/\t/\twww./' >>$file

    echo $end_token >> $file

    $restart_network
}

play()
{
    # removes $start_token-$end_token section
    # in any place of hosts file (not only in the end)
    sed_script="{
s/$end_token/$end_token/
t finished_sites

s/$start_token/$start_token/
x
t started_sites

s/$start_token/$start_token/
x
t started_sites

p
b end
: started_sites
d
: finished_sites
x
d
: end
d
}"
    # if no hosts file found...
    [ -e "$1" ] || exit_with_error $E_NO_HOSTS_FILE "No hosts file found"

    file=$1

    sed --in-place -e "$sed_script" $file

    $restart_network
}

# check for input parameters
[[ "$#" -eq 0 ]] && exit_with_error $E_NO_PARAMS "No parameters given"

curr_user=$(trim $(whoami))
curr_user=$(to_lower $curr_user)

# run fron root user
# to change hosts file
[ $curr_user == "root" ] || exit_with_error $E_USER_NOT_ROOT "Please, run from root"


uname=$(trim `uname`)

if [ "Linux" == $uname ]; then
    restart_network="/etc/init.d/networking restart"
elif [ "Darwin" == $uname ]; then
    restart_network="dscacheutil -flushcache"
else
    message="Please, contribute DNS cache flush command on GitHub"
    restart_network="echo $message"
fi

##############################

hosts_file="/etc/hosts"
start_token="## start-gsd"
end_token="## end=gsd"

action=$1

case "$action" in
    "play")
        play $hosts_file; ;;
    "work")
        work $hosts_file; ;;
        *) exit_with_error $E_WEIRD_PARAMS "Some weird params given" ;;
esac

