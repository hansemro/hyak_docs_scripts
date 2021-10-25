#!/usr/bin/env bash

# touch_all.sh: Touches all the files and directories in the given directory

# Usage: ./touch_all.sh </path/to/dir/>
#
# Examples: ./touch_all.sh /gscratch/scrubbed/<NETID>

if [ $1 ]; then
    #find "$1" -print -exec touch {} \;
    find "$1" -exec touch {} \;
else
    echo "Pass directory as argument to touch"
fi
