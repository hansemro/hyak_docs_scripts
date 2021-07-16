Tutorial: Running GUI Applications on HYAK
==========================================

Maintained by Hansem Ro (`hansemro@outlook.com`).

This tutorial will cover steps to run GUI applications via X11 forwarding, a
graphical desktop environment (via X11 forwarding or VNC), and basic
troubleshooting steps.

## Setup

In general, users will need the following:

- SSH client
- X11 server
- VNC client

### Windows

#### MobaXterm

[MobaXterm](https://mobaxterm.mobatek.net/) provides a Cygwin environment with
SSH, X11, and VNC capabilities in one package.

#### Standalone Alternatives for Windows 10 Users

These are just my personal recommendations.

- [OpenSSH Client for Windows](https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse)
    - Create `/dev/tty` to fix known [issue](https://github.com/PowerShell/Win32-OpenSSH/issues/1088) by running the following in an admin powershell: `mkdir /dev && echo x > /dev/tty`
    - Set DISPLAY environment variable to `localhost:0.0`
- [VcXsrv](https://sourceforge.net/projects/vcxsrv/files/vcxsrv/)
- [TightVNC (non-Java version)](https://www.tightvnc.com/)
    - Install VNC Viewer
- [(Optional) Windows Terminal](https://www.microsoft.com/en-us/p/windows-terminal/9n0dx20hk701)

### macOS

Since macOS provides ssh and VNC capabilities, macOS users will just need to
install [XQuartz](https://www.xquartz.org/).

### Linux

Debian/Ubuntu:

```
sudo apt-get install vinagre openssh-client xinit xterm xnest
```

RHEL8/CentOS8:

```
sudo yum install vinagre xterm openssh-clients \
        xorg-x11-{server-Xorg,server-utils,xinit-session} \
        xorg-x11-{utils,xauth,drivers,xbitmaps,xkb-utils} \
        xorg-x11-server-Xnest
```

## Running a GUI App via X11 Forwarding

Steps for all OS variants are similar. The general procedure goes as follows:

1. Launch X server
2. SSH into HYAK with X11 forwarding
3. Connect to an interactive node with X11 forwarding
4. Launch X application

### Windows (MobaXterm)

Create an SSH session: Sessions -> New Session -> SSH

Set remote host as `klone.hyak.uw.edu` and your UW NetID as your username.

Under `Advanced SSH Settings`, ensure the X11-Forwarding is checked.

Press OK and login.

Test X11 forwarding by running `xeyes` in the login node and an interactive
node:

```
[<NETID>@klone1 ~]$ xeyes
...
[<NETID>@klone1 ~]$ srun --x11 -p compute -A stf --nodes=1 --ntasks-per-node=4 --time=2:00:00 --mem=8G --pty /bin/bash
...
[<NETID>@nXXXX ~]$ xeyes
...
```

### Windows (VcXsrv)

TODO

### macOS

TODO

### Linux

Connect to Hyak with X11 forwarding.

```
ssh -Y <NETID>@klone.hyak.uw.edu
```

Connect to an interactive node.

```
srun --x11 -p compute -A stf --nodes=1 --ntasks-per-node=4 --time=2:00:00 --mem=8G --pty /bin/bash
```

Test X11 forwarding with `xeyes`.

Example: Matlab GUI

```
module load matlab
matlab &
```

## Running a graphical desktop environment via X11 Forwarding

(Windows and macOS users can skip this step.) Linux users will need to take an
additional step to prepare a nested X server window. On the local machine, run
the following:

```
Xnest :2 &
export DISPLAY=:2
```

Proceed with a guide to run a GUI app via X11 Forwarding above.

Obtain or build an XFCE singularity container. (Users can replace XFCE with
another graphical environment by modifying the provided recipe.)

```bash
# inside an interactive node and not in a login node 
git clone git@bitbucket.org:psy_lab/xfce_singularity.git
cd xfce_singularity

# build xfce.sif container
make
```

Launch desktop environment from an interactive node.

```
$ singularity shell xfce.sif
Singularity> unset DBUS_SESSION_BUS_ADDRESS
Singularity> startxfce4 &
```

Example: Matlab GUI

Create a terminal window in the XFCE session and run the following:

```
ssh -Y $(hostname)
module load matlab
matlab &
```

## Running a graphical desktop environment via VNC

The VNC method requires forwarding ports from the interactive node to the
user's system. 

### Windows (MobaXterm)

In MobaXterm, start a local terminal and run the following.

```
$ ssh -L 59000:127.0.0.1:5901 <NETID>@klone.hyak.uw.edu
[<NETID>@klone1 ~]$ salloc --x11 -p compute -A stf --nodes=1 --ntasks-per-node=4 --time=2:00:00 --mem=8G
[<NETID>@klone1 ~]$ ssh -L 5901:127.0.0.1:5901 $SLURM_NODELIST
```

Obtain or build an XFCE singularity container. (Users can replace XFCE with
another graphical environment by modifying the provided recipe.)

```bash
# inside an interactive node and not in a login node 
git clone git@bitbucket.org:psy_lab/xfce_singularity.git
cd xfce_singularity

# build xfce.sif container
make

# copy xstartup to ~/.vnc/xstartup
mkdir -p ~/.vnc
cp xstartup ~/.vnc/xstartup
chmod +x ~/.vnc/xstartup
```

Enter `xfce.sif` container and run the following:

```bash
# set vnc password
vncpasswd

# start vncserver
vncserver &
```

In MobaXterm, connect to the VNC session forwarded to `localhost:59000`.

Since the XFCE container contains a limited number of applications, you can ssh
into the interactive node with X11 Forwarding to run additional applications
(including ones from `modules avail` and other singularity containers). To load
Matlab, for example, open a terminal window in the VNC session and run the
following:

```bash
ssh -Y $(hostname)

# run the command below if you want the GUI applications drawn inside the VNC
# client.
export DISPLAY=:1

module load matlab
matlab &
```

### Windows (TightVNC Viewer)

TODO

### macOS

TODO

### Linux

Connect to a Hyak interactive node with port forwarding.

```
ssh -L 59000:127.0.0.1:5901 <NETID>@klone.hyak.uw.edu
[<NETID>@klone1 ~]$ salloc --x11 -p compute -A stf --nodes=1 --ntasks-per-node=4 --time=2:00:00 --mem=8G
[<NETID>@klone1 ~]$ ssh -L 5901:127.0.0.1:5901 $SLURM_NODELIST
```

Obtain or build an XFCE singularity container. (Users can replace XFCE with
another graphical environment by modifying the provided recipe.)

```bash
# inside an interactive node and not in a login node 
git clone git@bitbucket.org:psy_lab/xfce_singularity.git
cd xfce_singularity

# build xfce.sif container
make

# copy xstartup to ~/.vnc/xstartup
mkdir -p ~/.vnc
cp xstartup ~/.vnc/xstartup
chmod +x ~/.vnc/xstartup
```

Enter `xfce.sif` container and run the following:

```bash
# set vnc password
vncpasswd

# start vncserver
vncserver &
```

With a VNC client (such as vinagre), connect to the VNC session at `localhost:59000`.

### Cleanup Routine

1. Kill VNC session:

`vncserver -kill :1`

2. Exit interactive node (and give up node access manually if using salloc to access node)

```
[<NETID>@nXXXX PATH]: exit

# run if exiting the node does not deallocate the node. 
# run "squeue | grep $USER" to check for active work sessions.
[<NETID>@klone1 PATH]: scancel $SLURM_JOB_ID
```

3. Exit login node to stop the port forward.

## Troubleshooting

### 'Can't open display: ...'

This error can appear for several reasons:

1. X server is not running.

2. DISPLAY environment variable is not set or is set incorrectly.

3. X11-forwarding is not enabled.
