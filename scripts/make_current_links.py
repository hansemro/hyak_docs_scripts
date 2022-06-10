#!/usr/bin/env python3

# Written by Hansem Ro <hansemro@outlook.com> Dec. 16, 2021
# Updated by Hansem Ro <hansemro@outlook.com> Jun. 9, 2022

# This script creates/updates $EDA_TOOLS_PATH/<tool_name>/current symlinks
# to the version of the latest-installed tool.

# Instructions:
# 1) Set EDA_TOOLS_PATH environment variable (ensure you have proper permissions)
# 2) Run script with python3: `python3 make_current_links.py`

import os
from glob import glob

tools_path = os.getenv("EDA_TOOLS_PATH")
if not tools_path:
    print("Error: EDA_TOOLS_PATH environment variable not defined")
    exit(1)

for tool in glob(f"{tools_path}/*"):
    ver_max = ""
    time_max = 0
    for ver in glob(f"{tool}/*"):
        if "current" not in ver:
            time = os.path.getctime(ver)
            if time > time_max:
                ver_max = ver
                time_max = time
        else:
            os.remove(ver)
    if time_max > 0 and ver_max is not "":
        ver_max = os.path.basename(ver_max)
        # make link
        cmd = f"cd {tool} && ln -s {ver_max} current"
        print(cmd)
        err = os.system(cmd)

exit(0)
