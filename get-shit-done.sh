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

    # add sites from ini file
    # to site_list array
    sites_from_ini $ini_file

    file="$1"
    
    # check if work mode has been set
    if grep $start_token $file &> /dev/null; then
        if grep $end_token $file &> /dev/null; then
            exit_with_error $E_ALREADY_SET "Work mode already set."
        fi
    fi

    echo $start_token >> $file

    for site in "${site_list[@]}"
    do
        echo -e "127.0.0.1\t$site" >> $file
        echo -e "127.0.0.1\twww.$site" >> $file
    done

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

sites_from_ini()
{
    [ -e "$1" ] || return 1

    # read all lines from ini file
    while read line
    do
        # split the equals sign
        arr=( ${line/=/" "} )
        key=${arr[0]}
        value=${arr[1]}

        # just save sites variable
        if [ "sites" == $key ]; then
            # remove trailing commas
            clean_arr=$(echo "$value" | sed "s/,*$//")
            # and leading
            clean_arr=$(echo "$clean_arr" | sed "s/^,*//")
            sites_arr=$(echo $clean_arr | tr ',' "\n")

            # get array size
            count=${#site_list[*]}

            # add all sites to global sites array 
            for site in $sites_arr
            do
                site_list[$count]=$site
                ((count++))
            done
        fi
        
    done < "$1"
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

