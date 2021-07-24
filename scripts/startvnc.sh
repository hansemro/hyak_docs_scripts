#!/usr/bin/env bash
# Maintained by Hansem Ro <hansemro@outlook.com>

# Version: 0.1

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


# quit immediately if a process fails
set -e

# quit if vnc password is not set
if ! [ -f "$HOME"/.vnc/passwd ]; then
    echo "Error: VNC password is not set"
    echo ""
    exit 1
fi

# quit if a vnc session exists
VNC_JOBID=$(squeue | grep "$USER" | grep "vnc" | awk '{print $1}')
if [ $VNC_JOBID ] || [ -f .tmp_jobid ] || [ -f .tmp_node ]; then
    echo "Error: VNC server already running"
    exit 1
fi

XFCE_CONTAINER_FILEPATH="$HOME"/xfce_singularity/xfce.sif
CMD_STARTVNC="singularity exec $XFCE_CONTAINER_FILEPATH \
    vncserver -depth 24 -geometry 1920x1080 &"

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

# start vncserver and forward port 5901
ssh "$NODE" "$CMD_STARTVNC"
ssh -N -f -L 5901:127.0.0.1:5901 "$NODE" &
