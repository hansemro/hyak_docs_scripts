Tutorial: Running HYAK and EDA Tools
==========================================

This tutorial will cover steps to use the EDA Tools in Hyak.

## Starting VNC session

Connect to Hyak login node.

```
$ ssh <NETID>@klone.hyak.uw.edu
```

## Setup tcsh as your default Unix shell (JUST ONE TIME)

Open the file `$HOME/.bash_profile` and add the following lines.

```bash
WHICH_TCSH=`which tcsh`

if [ $WHICH_TCSH != "" ]
then
  echo "tcsh found - switching..."
  exec tcsh
fi
```

Close your current connection to hyak and open a new ssh session. It should use tcsh as a default Unix shell.

## Setup hyakvnc.py alias (JUST ONE TIME)

The script **hyakvnc.py** is located in `/gscratch/ece/hyak_docs/scripts`. To use easily this script, the best option is to create an alias for this script. To create an alias, create/modify the file `$HOME/.aliases.csh` in you `$HOME` directory.

Add the following line in `.aliases.csh`:

```tcsh
alias hyakvnc '/gscratch/ece/hyakvnc.py'
```

Also be sure to source this file in `$HOME/.cshrc`.  Add this line in the `.cshrc` file:

```tcsh
source $HOME/.aliases.csh
```

Finally, source again the `.cshrc` file with  the following command

```
source $HOME/.cshrc
```

## Explore hyakvnc.py utility

Run hyakvnc.py with `-h` to see all available options.

```
[<NETID>@klone]$ hyakvnc -h
usage: hyakvnc.py [-h] [-p PARTITION] [-A ACCOUNT] [-J JOB_NAME]
                  [--timeout TIMEOUT] [--port U2H_PORT] [-t TIME] [-c CPUS]
                  [--mem MEM] [--status] [--kill KILL_JOB_ID] [--kill-all]
                  [--set-passwd] [--container SING_CONTAINER] [-d] [-f] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -p PARTITION, --partition PARTITION
                        Slurm partition
  -A ACCOUNT, --account ACCOUNT
                        Slurm account
  -J JOB_NAME           Slurm job name
  --timeout TIMEOUT     Allocation timeout length (in seconds)
  --port U2H_PORT       User<->Hyak Port
  -t TIME, --time TIME  Subnode reservation time (in hours)
  -c CPUS, --cpus CPUS  Subnode cpu count
  --mem MEM             Subnode memory
  --status              Print VNC jobs and other details, and then exit
  --kill KILL_JOB_ID    Kill specified VNC session, cancel its VNC job, and
                        exit
  --kill-all            Kill all VNC sessions, cancel VNC jobs, and exit
  --set-passwd          Prompts for new VNC password and exit
  --container SING_CONTAINER
                        XFCE+VNC Singularity Container (.sif)
  -d, --debug           Enable debug logging
  -f, --force           Skip node check and create a new VNC session
  -v, --version         Print program version and exit
```

### Request interactive node and create VNC session

To create VNC session on an interactive node with the default parameters of the script run:

```
[<NETID>@klone]$ hyakvnc
```

The default parameters are:

| Parameter | Default |
| :-------: | :--:    |
| CPU       | 8       |
| MEM(RAM)  | 16      |
| TIME      | 4 Hours |
| Container | Centos7 |
| Account   | ece     |

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

To modify the default parameters just add the argument to change. An example could be:

```
[<NETID>@klone]$ hyakvnc --mem 64G -t 12
```

It requests an interactive node with the default parameters but changes the Memory request to 64G and 12 Hours.

#### Stopping VNC session

To stop VNC session and its associated job, run hyakvnc.py with `--kill-all`
option.

```
[<NETID>@klone]$ hyakvnc.py --kill-all
```
