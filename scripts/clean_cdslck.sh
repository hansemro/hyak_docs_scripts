#!/usr/bin/env bash

# clean_cdslck.sh: Clean *.cdslck files in passed cadence directory

# Usage: ./clean_cdslck.sh /path/to/cadence_dir/

if [ $1 ]; then
    find $1 -type f -name '*.cdslck*' -exec rm {} +
fi
