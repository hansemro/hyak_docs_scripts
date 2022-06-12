Tutorial: Running GUI Applications on HYAK
==========================================

Maintained by Hansem Ro (`hansemro@outlook.com`).

This tutorial will cover steps to run GUI applications via X11 forwarding, a
graphical desktop environment (via X11 forwarding or VNC), and basic
troubleshooting steps.

Follow this tutorial by fulfilling the requirements in [Setup](# Setup) and
selecting one of the three methods of reaching a graphial user interface:

1. Running GUI applications with X11-Forwarding (w/o desktop environment).

2. Running desktop environment with X11-Forwarding.

3. Running desktop environment with VNC.

The last (VNC) method can survive disconnects from the server since the X
server is running on Hyak. Because of this and that VNC method achieves lower
latency, VNC method is preferred for general use.

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

```bash
sudo apt-get install vinagre openssh-client xinit xterm xnest
```

RHEL8/CentOS8:

```bash
sudo yum install vinagre xterm openssh-clients \
        xorg-x11-{server-Xorg,server-utils,xinit-session} \
        xorg-x11-{utils,xauth,drivers,xbitmaps,xkb-utils} \
        xorg-x11-server-Xnest
```

## (Option 1) Running a GUI App via X11 Forwarding

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
[<NETID>@klone]$ xeyes
...
[<NETID>@klone]$ srun --x11 -p <partition> -A <account> -c 16 --time=2:00:00 --mem=8G --pty /bin/bash
...
[<NETID>@<node_name>]$ xeyes
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
srun --x11 -p <partition> -A <account> -c 16 --time=2:00:00 --mem=8G --pty /bin/bash
```

Test X11 forwarding with `xeyes`.

Example: Matlab GUI

```
module load matlab
matlab &
```

## (Option 2) Running a graphical desktop environment via X11 Forwarding

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

```bash
ssh -Y $(hostname)
module load matlab
matlab &
```

## (Option 3) Running a graphical desktop environment via VNC

### (Recommended) Setup VNC with hyakvnc.py utility

Run hyakvnc.py with `-h` to see all available options.

#### Starting VNC session

Connect to Hyak login node.

```
$ ssh <NETID>@klone.hyak.uw.edu
```

To create VNC session on an interactive node with 16 cores, 16G RAM, and
allocated for 3 hours, run the following:

```
[<NETID>@klone]$ ./hyakvnc.py -c 16 --mem 16G -t 3
```

If not done already, this utility may ask the user to prepare for SSH
intracluster access and VNC password. Both are required for this utility.

If the utility succeeded, it should output additional instructions to set up
a single port forward from the user machine to Hyak login node.

Example:
```
...
Successfully created port forward
=====================
Run the following in a new terminal window:
        ssh -N -f -L 5900:127.0.0.1:5900 hansem7@klone.hyak.uw.edu
then connect to VNC session at localhost:5900
=====================
```

Run the instructed ssh port forward command in a new terminal session (on
the user machine).

Lastly, connect to VNC session at the instructed address (on user machine with VNC
client).

#### Stopping VNC session

To stop VNC session and its associated job, run hyakvnc.py with `--kill-all`
option.

```
[<NETID>@klone]$ ./hyakvnc.py --kill-all
```

### (Advanced) Manual setup

Because there is a network firewall, the user needs to make 2 port forwards to
establish VNC connection:

1. a port forward between login node and interactive node,

2. and a port forward between user machine and login node.

The second port forward (and subsequently, the first) will require the user to
find a port that is unused by another user/process.

Running `netstat -ant | grep LISTEN | grep <PORT>` with some port number can be
used to determine if a port is used. If netstat shows nothing for the given
port, the user may use that port.

#### Starting VNC session

Connect to Hyak login node.

```
$ ssh <NETID>@klone.hyak.uw.edu
```

Obtain or build an XFCE singularity container. (Users can replace XFCE with
another graphical environment by modifying the provided recipe.)

```bash
# inside an interactive node and not in a login node
git clone git@bitbucket.org:psy_lab/xfce_singularity.git
cd xfce_singularity

# build xfce.sif container
make
```

Allocate node with `salloc` and start vnc session inside the singularity
container.

```
[<NETID>@klone]$ salloc --no-shell -p <partition> -A <account> --time 2:00:00 --mem=8G -c 16
[<NETID>@klone]$ ssh <node_name|node_hostname|$(squeue | grep $USER | awk '{print $8}')>
[<NETID>@<node_name>]$ singularity shell ./xfce.sif
Singularity> vncserver -xstartup ./xstartup -baseHttpPort 5900
...
New '<node_hostname>:<vnc_display_number> (<NETID>)' desktop at :<vnc_display_number> on machine <node_hostname>
...
Singularity> exit
[<NETID>@<node_name>]$ exit
```

Get the VNC display number and add 5900 (base VNC port) to it (e.g. if VNC
display number is :1, then VNC port is at 5901). Now, we need to map this VNC
port to an unused port on the login node.

Find unused port starting at base VNC port 5900.

```
[<NETID>@klone]$ netstat -ant | grep LISTEN | grep 5900
tcp        0      0 127.0.0.1:5900          0.0.0.0:*               LISTEN
tcp6       0      0 ::1:5900                :::*                    LISTEN
[<NETID>@klone]$ ss -l | grep 5901
tcp   LISTEN 0      128                                                                 127.0.0.1:5901                     0.0.0.0:*
tcp   LISTEN 0      128                                                                     [::1]:5901                        [::]:*
mptcp LISTEN 0      128                                                                 127.0.0.1:5901                     0.0.0.0:*
mptcp LISTEN 0      128                                                                     [::1]:5901                        [::]:*
[<NETID>@klone]$ netstat -ant | grep LISTEN | grep 5902
[<NETID>@klone]$ ss -l | grep 5902
[<NETID>@klone]$
```

Since netstat/ss with port 5902 shows nothing, we can use this for the second
port forward.

```
[<NETID>@klone]$ ssh -N -f -L 5902:127.0.0.1:<VNC display number + base port> <node_name>
```

In a new terminal window (on the user machine), create the second port forward with
the port checked with netstat.

```
$ ssh -N -f -L 5902:127.0.0.1:5902 <NETID>@klone.hyak.uw.edu
```

Now connect to VNC session on user machine at localhost:5902.

#### Stopping VNC session

Kill VNC server running on interactive node.

```
[<NETID>@klone]$ ssh <node_name|node_hostname|$(squeue | grep $USER | awk '{print $8}')>
[<NETID>@<node_name>] singularity shell xfce.sif
Singularity> vncserver -kill :*
Singularity> exit
[<NETID>@<node_name>] exit
```

Cancel VNC job.

```
[<NETID>@klone]$ scancel <job_id>
```

Lastly, kill port forward between user machine and Hyak.

TODO: Find command to complete this last step.

## Troubleshooting

### 'Can't open display: ...'

This error can appear for several reasons:

1. X server is not running.

2. DISPLAY environment variable is not set or is set incorrectly.

3. X11-forwarding is not enabled.

### Port forward failure: `bind: Address already in use`

This error occurs if the remote port is already used.

### `hyakvnc.py` hangs mid-way after allocation

Try deleting all entries with klone in `~/.ssh/authorized_keys` and try again.

### Cannot share clipboard to VNC session

1. Keep `vncconfig` open in VNC session as this window allows clipboard sharing.
    - If closed, run `vncconfig &` in the VNC session to reopen window.
2. Use VNC client that supports clipboard sharing.
    - macOS' VNC client does not have working clipboard sharing.
    - Download TigerVNC binary from https://sourceforge.net/projects/tigervnc/files/stable/1.12.0/
        - TigerVNC also supports resolution-resizing by changing window size.
