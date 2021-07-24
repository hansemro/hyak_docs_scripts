#!/usr/bin/env bash
# Maintained by Hansem Ro <hansemro@outlook.com>

# stopvnc.sh: Stop vnc session and close its associated node on Klone.
#
# Usage: ./stopvnc.sh

XFCE_CONTAINER_FILEPATH="$HOME"/xfce_singularity/xfce.sif
CMD1="singularity exec $XFCE_CONTAINER_FILEPATH vncserver -kill :*"

NODE=$(cat "$HOME"/.tmp_node)
JOBID=$(cat "$HOME"/.tmp_jobid)

ssh "$NODE" "$CMD1"
scancel "$JOBID"

rm "$HOME"/.tmp_node
rm "$HOME"/.tmp_jobid
