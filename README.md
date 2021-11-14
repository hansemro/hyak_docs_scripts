HYAK Docs and Tutorials
=======================

This repository contains documentation and tutorials regarding HYAK and its
usage.

## About HYAK

UW IT maintains two high-performance computing clusters that make up HYAK: Mox
and Klone. More information about the hardware can be found
[here](https://hyak.uw.edu/systems/).

Nodes and its resources (CPU cores, GPUs, memory, and storage) are allocated
and managed via [Slurm](https://slurm.schedmd.com/overview.html).

HYAK maintains a collection of software capabilities as modules (including
the capability to run Singularity containers). More information can be found
[here](https://hyak.uw.edu/docs/tools/modules) and
[here](https://hyak.uw.edu/docs/tools/containers).

## Getting access to HYAK

UW (STF paying) students can gain access by joining the UW Research Computing
Club. More information on account creation can be found
[here](https://hyak.uw.edu/docs/account-creation#i-have-a-pi-and-the-pi-contributed-hyak-nodes).

## Conecting to HYAK

SSH is the primary method of connecting and interacting with HYAK.
See more [here](https://hyak.uw.edu/docs/setup/ssh).

Mox: `ssh <NETID>@mox.hyak.uw.edu`

Klone: `ssh <NETID>@klone.hyak.uw.edu`

Note: While Duo two-factor authentication cannot be skipped via pubkey
authentication, Mac and Linux users may use SSH multiplexing to reuse an
autheticated connection and effectively bypass Duo for subsequent connections.

### [Mac/Linux] Setting up SSH Multiplexing to Skip Repeated Duo Authentication

Add the following to ~/.ssh/config on your system:
```
Host klone.hyak.uw.edu
    Hostname %h
    User <NETID>
    ControlPath ~/.ssh/%r@%h:%p
    ControlMaster auto
    ControlPersist 10m

Host n????
    Hostname %h
    User <NETID>
    ProxyJump klone.hyak.uw.edu
```

With SSH-mux prepared, you may also use pubkey authentication in place of
standard password authentication.

## Usage Guidance

Upon connecting to Hyak via ssh, a login node shell becomes accessible. From
here, you can manage other nodes with slurm commands and run programs.

In general, login nodes should not be used for computational tasks or GUI
programs. Login nodes serve as an interface to Hyak compute nodes and should
be used for the following situations:

- file transfers between Hyak and external source (another computer, internet)
- text editing
- slurm management
- light programs

For heavy workloads or GUI programs or containerized programs, a compute node
should be used instead.

## Storage Guidance

User home directories (`/mmfs1/home/<NETID>`) are limited to 10 GB!

Users have access to mounted storage on `/gscratch/stf/<NETID>` and
`/gscratch/scrubbed/<NETID>`. If a directory does not exist, then just create
it.

More information about storage can be found
[here](https://hyak.uw.edu/docs/storage/gscratch).

## Recommendations

### [Create SSH keys for intracluster access](https://hyak.uw.edu/docs/setup/ssh#intracluster-ssh-keys)

In Klone shell, run the following:

```
ssh-keygen -C klone -t rsa -b 2048 -f ~/.ssh/id_rsa -q -N ""
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

This essentially skips password authentication when connecting between nodes.

### .bashrc Additions for Singularity

```
export PATH=/opt/ohpc/pub/libs/singularity/3.7.1/bin:$PATH
export SINGULARITY_BINDPATH="/tmp:/tmp,$HOME,$PWD,/mmfs1,/gscratch,/opt:/opt,/:/hyak_root"
```

## Tutorials

The `./tutorials/` directory provides some Hyak-related tutorials.

- [GUI Tutorial (X11,VNC)](tutorials/gui.md)
