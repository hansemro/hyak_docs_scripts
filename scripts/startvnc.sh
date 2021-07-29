#!/usr/bin/env bash
# Maintained by Hansem Ro <hansemro@outlook.com>

# Version: 0.2

# startvnc.sh: Starts a VNC session with XFCE from Klone login node.
#
# Initial setup: Building XFCE container
#  $ srun -p compute -A stf --nodes=1 --ntasks-per-node=4 --time=1:00:00 --mem=8G --pty /bin/bash
#  $ cd ~/
#  $ git clone git@bitbucket.org:psy_lab/xfce_singularity.git
#  $ cd xfce_singularity
#  $ make
#
# Usage: ./startvnc.sh
#
# To stop a vnc session, run the companion script stopvnc.sh in a login node.

XFCE_CONTAINER_FILEPATH=/gscratch/ece/xfce_singularity/xfce.sif
CMD_STARTVNC="singularity exec $XFCE_CONTAINER_FILEPATH \
    vncserver -depth 24 -geometry 1920x1080 &"

# quit immediately if a process fails
set -e

# quit if vnc password is not set
if ! [ -f "$HOME"/.vnc/passwd ]; then
    echo "Error: VNC password is not set"
    echo "To set vnc password, run the following:"
    echo "singularity exec $XFCE_CONTAINER_FILEPATH vncpasswd"
    exit 1
fi

# quit if a vnc session exists
VNC_JOBID=$(squeue | grep "$USER" | grep "vnc" | awk '{print $1}')
if [ $VNC_JOBID ] || [ -f .tmp_jobid ] || [ -f .tmp_node ]; then
    echo "Error: VNC server already running"
    exit 1
fi

# allocate compute node for running vnc server (for 3 hours)
salloc -J vnc --no-shell -p compute -A stf --nodes=1 \
    --ntasks-per-node=4 --time=3:00:00 --mem=8G

# find compute node's hostname and jobid
JOBID=$(squeue | grep "$USER" | grep "vnc" | awk '{print $1}')
NODE=$(squeue | grep "$USER" | grep "vnc" | awk '{print $8}')

# save running hostname and jobid to tmp files
echo "$JOBID" > "$HOME"/.tmp_jobid
echo "$NODE" > "$HOME"/.tmp_node

# TODO set vnc password if ~/.vnc/passwd does not exist

# start vncserver and forward vnc port
VNC_PORT=5900
TMP=$(ssh "$NODE" "$CMD_STARTVNC")
OFFSET=$(echo $TMP | sed -E "s/(New\s)('[^']+'\sdesktop\sat\s):([^\s]+)/\3/" | awk '{print $1}')
((VNC_PORT=VNC_PORT + OFFSET))
echo "VNC server port: $VNC_PORT"
ssh -N -f -L "$VNC_PORT":127.0.0.1:"$VNC_PORT" "$NODE" &
echo "Create a port between your system and Hyak by running the following"\
    "on a local terminal session (leave running in background):"
echo "ssh -N -f -L 59000:127.0.0.1:$VNC_PORT $USER@klone.hyak.uw.edu"
