#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

VERSION = 0.4

# Created by Hansem Ro <hansem7@uw.edu> <hansemro@outlook.com>
# Maintained by ECE TAs

# TODO: Usage Guide
# Usage: ./hyakvnc.py [-h/--help] [OPTIONS]

# Installing dependencies with containers:
#   $ singularity shell /gscratch/ece/xfce_singularity/xfce.sif
#   $ pip3 install --user setuptools
#   $ pip3 install --user wheel
#   $ pip3 install --user psutil
#
# Or run:
#   $ ./setup.sh
#

import argparse # for argument handling
import logging # for debug logging
import time # for sleep
import psutil # for netstat utility
import os
import subprocess # for running shell commands
import re # for regex

# tasks:
# - [x] user arguments to control hours
# - [x] user arguments to close active vnc sessions and vnc slurm jobs
# - [x] user arguments to override automatic port forward (with conflict checking)
# - [x] reserve node with slurm
# - [x] start vnc session (also check for active vnc sessions)
# - [1/2] identify used ports : current implementation needs improvements
# - [x] map node<->login port to unused user<->login port
# - [x] port forward between login<->subnode
# - [x] print instructions to user to setup user<->login port forwarding

BASE_VNC_PORT = 5900
LOGIN_NODE_LIST = ["klone1.hyak.uw.edu", "klone2.hyak.uw.edu"]
SINGULARITY_BIN = "/opt/ohpc/pub/libs/singularity/3.7.1/bin/singularity"
XFCE_CONTAINER = "/gscratch/ece/xfce_singularity/xfce.sif"
XSTARTUP_FILEPATH = "/gscratch/ece/xfce_singularity/xstartup"

class node:
    def __init__(self, name, debug=False):
        self.debug = debug
        self.name = name
        self.cmd_prefix = SINGULARITY_BIN + " exec " + XFCE_CONTAINER

class sub_node(node):
    def __init__(self, name, job_id, debug=False):
        super().__init__(name, debug)
        self.hostname = name + ".hyak.local"
        self.job_id = job_id
        self.vnc_display_number = None
        self.vnc_port = None

    def print_props(self):
        print("Subnode properties:")
        props = vars(self)
        for item in props:
            msg = f"{item} : {props[item]}"
            print(f"\t{msg}")
            if self.debug:
                logging.debug(msg)

    def run_command(self, command:str):
        """
        Run command (with arguments) on subnode

        Args:
          command:str : command and its arguments to run on subnode

        Returns ssh subprocess with stderr->stdout and stdout->PIPE
        """
        assert self.name is not None
        if self.debug:
            print(["ssh", self.hostname, command])
            logging.debug(["ssh", self.hostname, command])
        return subprocess.Popen(["ssh", self.hostname, command], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # TODO: Find active VNC session
    def check_vnc(self):
        pass

    def start_vnc(self):
        """
        Starts VNC session

        Returns True if VNC session was started successfully and False otherwise
        """
        vnc_cmd = f"{self.cmd_prefix} vncserver -xstartup {XSTARTUP_FILEPATH} -baseHttpPort {BASE_VNC_PORT} -depth 24 &"
        check_cmd = f"{self.cmd_prefix} vncserver -list"
        proc = self.run_command(vnc_cmd)
        if self.debug:
            logging.debug(str(proc.communicate()[0], 'utf-8'))

        # get display number and port number
        check_proc = self.run_command(check_cmd)
        time.sleep(2)
        timer = 15
        while timer > 0:
            line = str(check_proc.stdout.readline(), 'utf-8')

            # TODO: check if this breaks prematurely
            if not line:
                break

            if self.debug:
                logging.debug(f"line: {line}")
            if ":" in line[0]:
                pattern = re.compile("""
                        (:)(?P<display_number>[0-9]+)
                        """, re.VERBOSE)
                match = re.match(pattern, line)
                assert match is not None
                self.vnc_display_number = int(match.group("display_number"))
                self.vnc_port = self.vnc_display_number + BASE_VNC_PORT
                if self.debug:
                    logging.debug("Obtained display number: {self.vnc_display_number}")
                    logging.debug("Obtained VNC port: {self.vnc_port}")
                return True
            time.sleep(1)
            timer = timer - 1
        if self.debug:
            logging.debug("Failed to start vnc session (Timeout/?)")
        print("start_vnc: Error: Timed out...")
        return False

    def kill_vnc(self, display_number=None):
        """
        Kill specified VNC session with given display number or all VNC sessions.
        """
        if display_number is None:
            target = ":*"
        else:
            assert display_number is not None
            target = ":" + str(display_number)
        if self.debug:
            print(f"Attempting to kill VNC session {target}")
            logging.debug(f"Attempting to kill VNC session {target}")
        cmd = self.cmd_prefix + " vncserver -kill " + target
        self.run_command(cmd)

class login_node(node):
    def __init__(self, name, debug=False):
        assert os.path.exists(XSTARTUP_FILEPATH)
        assert os.path.exists(SINGULARITY_BIN)
        assert os.path.exists(XFCE_CONTAINER)
        super().__init__(name, debug)
        self.subnode = None

    def find_node(self):
        """
        Returns a set with [subnode_name, job_id] pairs and returns None otherwise
        """
        ret = set()
        command = f"squeue | grep {os.getlogin()} | grep vnc"
        proc = subprocess.Popen(command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        while True:
            line = str(proc.stdout.readline(), 'utf-8')
            if not line:
                if not ret:
                    return None
                return ret
            if os.getlogin() in line:
                pattern = re.compile("""
                        (\s+)
                        (?P<job_id>[0-9]+)
                        (\s+[^ ]+\s+[^ ]+\s+[^ ]+\s+[^ ]+\s+[^ ]+\s+[^ ]+\s+)
                        (?P<subnode_name>n[0-9]{4})
                        """, re.VERBOSE)
                match = pattern.match(line)
                assert match is not None
                name = match.group("subnode_name")
                job_id = match.group("job_id")
                if self.debug:
                    msg = f"Found active subnode {name} with job ID {job_id}"
                    logging.debug(msg)
                ret.add((name, job_id))
        return None

    def check_vnc_passwd(self):
        """
        Returns True if vnc password is set and False otherwise
        """
        return os.path.exists(os.path.expanduser("~/.vnc/passwd"))

    def set_vnc_password(self):
        """
        Set VNC password
        """
        cmd = self.cmd_prefix + " vncpasswd"
        subprocess.call(cmd, shell=True)

    def run_command(self, command):
        if isinstance(command, list):
            return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        elif isinstance(command, str):
            return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def reserve_node(self, res_time=3, timeout=10, mem="16G", partition="compute-hugemem", account="ece"):
        """
        Reserves a node and waits until the node has been acquired.

        Args:
          res_time: Number of hours to reserve sub node
          timeout: Number of seconds to wait for node allocation
          mem: Amount of memory to allocate (Examples: "8G" for 8GiB of memory)
          partition: Partition name (see `man salloc` on --partition option for more information)
          account: Account name (see `man salloc` on --account option for more information)

        Returns sub_node object if it has been acquired successfully and None otherwise.
        """
        proc = subprocess.Popen(["salloc", "-J", "vnc", "--no-shell", "-p", partition,
            "-A", account, "-t", str(res_time) + ":00:00", "--mem=" + mem], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        timer = timeout
        alloc_stat = False

        print("Allocating node...")
        while not alloc_stat and timer > 0:
            print("...")
            line = str(proc.stdout.readline(), 'utf-8').strip()
            if self.debug:
                msg = f"line: {line}"
                print(msg)
                logging.debug(msg)
            if "Granted job allocation" in line:
                pattern = re.compile("""
                        (salloc:\sGranted\sjob\sallocation\s)
                        (?P<job_id>[0-9]+)
                        """, re.VERBOSE)
                match = pattern.match(line)
                subnode_job_id = match.group("job_id")
            elif "are ready for job" in line:
                pattern = re.compile("""
                        (salloc:\sNodes\s)
                        (?P<node_name>n[0-9]{4})
                        (\sare\sready\sfor\sjob)
                        """, re.VERBOSE)
                match = pattern.match(line)
                subnode_name = match.group("node_name")
                alloc_stat = True
                break
            elif self.debug:
                msg = f"Skipping line: {line}"
                print(msg)
                logging.debug(msg)
            time.sleep(1)
            timer = timer - 1
        if proc.stdout is not None:
            proc.stdout.close()
        if proc.stderr is not None:
            proc.stderr.close()

        if not alloc_stat:
            print("Error: node allocation timed out.")
            self.cancel_node(job_id)
            return None

        assert subnode_job_id is not None
        assert subnode_name is not None
        self.subnode = sub_node(name=subnode_name, job_id=subnode_job_id, debug=self.debug)
        return self.subnode

    def cancel_node(self, job_id:int):
        """
        Cancel access to nodes given its associated job ID

        Reference:
            See `man scancel` for more information on usage
        """
        proc = subprocess.Popen(["scancel", str(job_id)], stdout=subprocess.PIPE)
        print(str(proc.communicate()[0], 'utf-8'))

    def check_port(self, port:int):
        """
        Returns True if port is unused and False if used.
        """
        if self.debug:
            logging.debug(f"Checking if port {port} is used...")
        netstat = psutil.net_connections()
        for entry in netstat:
            if self.debug:
                logging.debug(f"Checking entry: {entry}")
            if port == entry[3].port:
                return False
        return True

    def get_port(self):
        """
        Returns unused port number if found and None if not found.
        """
        for i in range(0,300):
            port = BASE_VNC_PORT + i
            if self.check_port(port):
                return port
        return None

    def create_port_forward(self, login_port:int, subnode_port:int):
        """
        Port forward between login node and subnode

        Args:
          login_port:int : Login node port number
          subnode_port:int : Subnode port number

        Returns ssh-portforward subprocess with stderr->stdout and stdout->PIPE
        """
        assert self.subnode is not None
        assert self.subnode.name is not None
        if self.debug:
            msg = f"Creating port forward: Login node({login_port})<->Subnode({subnode_port})"
            logging.debug(msg)
        return subprocess.Popen(["ssh", "-N", "-f", "-L", f"{login_port}:127.0.0.1:{subnode_port}", self.subnode.hostname], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def print_props(self):
        """
        Print all properties (including subnode properties)
        """
        print("Login node properties:")
        props = vars(self)
        for item in props:
            msg = f"{item} : {props[item]}"
            print(f"\t{msg}")
            if self.debug:
                logging.debug(msg)
            if item == "subnode" and props[item] is not None:
                props[item].print_props()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--partition',
                    dest='partition',
                    help='slurm partition',
                    type=str)
    parser.add_argument('-A', '--account',
                    dest='account',
                    help='slurm account',
                    type=str)
    parser.add_argument('--port',
                    dest='u2h_port',
                    help='User<->Hyak Port',
                    type=int)
    parser.add_argument('-t', '--time',
                    dest='time',
                    help='Sub node reservation time (in hours)',
                    type=int)
    parser.add_argument('--mem',
                    dest='mem',
                    help='Sub node memory',
                    type=str)
    parser.add_argument('--kill',
                    dest='kill',
                    action='store_true',
                    help='Kill all VNC sessions, cancel VNC nodes, and exit')
    parser.add_argument('--set-passwd',
                    dest='set_passwd',
                    action='store_true',
                    help='Prompts for new VNC password')
    parser.add_argument('-d', '--debug',
                    dest='debug',
                    action='store_true',
                    help='Enable debug logging')
    parser.add_argument('-f', '--force',
                    dest='force',
                    action='store_true',
                    help='Skip node check and create a new VNC session')
    parser.add_argument('-v', '--version',
                    dest='print_version',
                    action='store_true',
                    help='Print program version and exit')
    args = parser.parse_args()

    if args.print_version:
        print(f"hyakvnc.py {VERSION}")
        exit(0)

    # setup logging
    if args.debug:
        log_filepath = os.path.expanduser("~/hyakvnc.log")
        if os.path.exists(log_filepath):
            os.remove(log_filepath)
        logging.basicConfig(filename=log_filepath, level=logging.DEBUG)

    if args.debug:
        print("Arguments:")
        for item in vars(args):
            msg = f"{item}: {vars(args)[item]}"
            print(f"\t{msg}")
            logging.debug(msg)

    hostname = os.uname()[1]
    on_subnode = re.match("(n|g)([0-9]{4}).hyak.local", hostname)
    on_loginnode = hostname in LOGIN_NODE_LIST
    if on_subnode or not on_loginnode:
        print("Error: Please run on login node.")
        exit(1)

    # create login node object
    hyak = login_node(hostname, args.debug)

    # check for existing subnode
    node_set = hyak.find_node()
    if not args.kill and not args.force:
        if node_set is not None:
            for entry in node_set:
                print(f"Error: Found active subnode {entry[0]} with job ID {entry[1]}")
            exit(1)

    if args.kill:
        msg = "Killing all VNC sessions..."
        print(msg)
        if args.debug:
            logging.debug(msg)
        # kill all vnc sessions
        cmd = hyak.cmd_prefix + " vncserver -kill :*"
        subprocess.call(cmd, shell=True)
        if node_set is not None:
            for entry in node_set:
                tmp_job_id = entry[1]
                msg = f"Canceling job ID {tmp_job_id}"
                print(f"\t{msg}")
                if args.debug:
                    logging.debug(msg)
                hyak.cancel_node(tmp_job_id)
        exit(0)

    # set VNC password at user's request or if missing
    if not hyak.check_vnc_passwd() or args.set_passwd:
        print("Please set new VNC password...")
        hyak.set_vnc_password()

    # TODO: check for existing vnc session

    # TODO: check for port forwards

    # reserve node
    res_time = 3 # hours
    timeout = 10 # seconds
    mem = "16G"
    partition = "compute-hugemem"
    account = "ece"
    if args.mem is not None:
        mem = args.mem
    if args.account is not None:
        account = args.account
    if args.partition is not None:
        partition = args.partition
    if args.time is not None:
        res_time = args.time
    # TODO: allow node count override (harder to implement)
    subnode = hyak.reserve_node(res_time, timeout, mem, partition, account)
    if subnode is None:
        exit(1)

    print("Node reserved...")

    # start vnc
    print("Starting VNC...")
    ret = subnode.start_vnc()
    if not ret:
        hyak.cancel_node(subnode.job_id)
        exit(1)

    # get unused User<->Login port
    # CHANGE ME: NOT ROBUST
    if args.u2h_port is not None:
        assert hyak.check_port(args.u2h_port)
        hyak.u2h_port = args.u2h_port
    else:
        hyak.u2h_port = hyak.get_port()

    if args.debug:
        hyak.print_props()

    # create port forward between login and sub nodes
    print(f"Creating port forward: Login node({hyak.u2h_port})<->Subnode({subnode.vnc_port})")
    h2s_fwd_proc = hyak.create_port_forward(hyak.u2h_port, subnode.vnc_port)

    # print command to setup User<->Login port forwarding
    print("=====================")
    print("Run the following in a new terminal window:")
    print(f"    ssh -N -f -L {hyak.u2h_port}:127.0.0.1:{hyak.u2h_port} {os.getlogin()}@klone.hyak.uw.edu &")
    print(f"then connect to VNC session at localhost:{hyak.u2h_port}")
    print("=====================")

    exit(0)

if __name__ == "__main__":
    main()