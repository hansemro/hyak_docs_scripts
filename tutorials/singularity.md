Singularity Container Tutorial
==============================

Written and maintained by Hansem Ro (`hansemro@outlook.com`).

This tutorial covers the following topics:

0. [x] Singularity Purpose
1. [x] Container usage (on work node)
    - 1.1 [x] Bind Paths
2. [ ] Container instances
    - 2.1 [ ] Starting/stopping instance
    - 2.2 [ ] Checking instance(s)
    - 2.3 [ ] Entering instance
3. [ ] Writing and building containers
    - 3.1 [x] General guidance for writing container recipes
    - 3.2 [ ] Updating containers
    - 3.3 [ ] Sandbox containers

# 0. Singularity Purpose

Singularity is a container platform that enable unprivileged users to build and
run programs within containers (unlike Docker which requires root permissions).
As user guide states, Singularity "swaps the host [OS] for the one inside [your]
container"
(https://sylabs.io/guides/3.7/user-guide/bind_paths_and_mounts.html#overview).

The purpose of assembling containers comes from the desire to reproduce the
working environments needed to run programs independent of what is installed on
the host system. So a container that works on one system works on a very
different system. Because of this property, tools that rely on dynamically-
linked libraries (and other dependencies) that are not present on the host
system can be made to work with the right container.

## Note: The target program need not be within the container.

Container developers usually package the target tool within the container, but
this may not always be the case. Sometimes the target tool lies outside the
container and on the host system. Because of this, containers can be designed
to target several tools by providing them with the requisite libraries and
dependencies.

# 1. Container usage (on work node)

Note: On Hyak, please use singularity on a work node and not on a login node.

On Hyak (work node), singularity is accessed via Environment Modules by running
the following:

```
module load singularity
```

To enter an interactive shell within the (.sif) container, run the following:

```
[<NETID>@nXXXX]$ singularity shell /path/to/singularity.sif
Singularity> echo "I am running inside the container!"
```

To execute a command (with arguments) within the container, run the following:

```
singularity exec /path/to/singularity.sif <COMMAND> <ARGS>
```

## 1.1 Bind Paths

See more about this topic [here](https://sylabs.io/guides/3.7/user-guide/bind_paths_and_mounts.html).

When you enter a container without specifying bind paths, certain paths may
become inaccessible (like `/gscratch` and `/mmfs1/home/<NETID>`).

To mount or bind paths on host to the container environment, specify directories
to bind in `$SINGULARITY_BINDPATH` prior to running `singularity <exec|shell>`.

```
export SINGULARITY_BINDPATH="/tmp:/tmp,$HOME,$PWD,<source>[:<dest>]"
```

# 2. Container instances

TODO

## 2.1 Starting/stopping instance

TODO

```
singularity instance start /path/to/container.sif <instance_name>
```

```
singularity instance stop <instance_name>
```

## 2.2 Checking instance(s)

TODO

```
singularity instance list
```

## 2.3 Entering instance

TODO

```
singularity [shell|exec] [OPTIONS] instance://<instance_name>
```

# 3. Writing and building containers from scratch

Without administrative privileges, singularity containers can be built from
recipe files by the following command:

```
singularity build --fakeroot <output_image.sif> <recipe.def>
```

Recipe def files are plain-text files with a Header and one or more Sections
starting with %. Header describes the base container Linux distribution (such
as Ubuntu 18.04 or Rocky Linux 8). Sections describe additional steps on top
of the base installation for additional functionality.

## 3.1 General guidance for writing container recipes

To avoid wasting time tweaking and re-building container images, follow these
general guidelines:

1. Get or generate a dependency list for the tools you want to run.
    - `ldd <path_to_exec>` prints matched and unmatched dynamic library dependencies
    - `strace <cmd>` can identify libraries failing to be found or loaded.
2. If installing tools manually, find ways to install them entirely through the commandline.
    - Pipe echo/printf statements to handle user-interactions in installers.
3. Install/Use library dependencies from tool vendor if possible or closest version from distro package manager.
    - Example: Synopsys VCS+DVE require vendor-provided GCC and scripts to be installed in a particular way.
    - Example: Cadence Virtuso provides library dependencies for Ubuntu.
    - Info: You can prioritize vendor-provided libraries by prepending `$LD_LIBRARY_PATH` with vendor library path.
4. Avoid installing large tools in containers since image compression takes a significant amount of time.

### Header

Header, which is written at the top of the def/recipe file, is used to describe
the container OS and installation source/agent.

```
Bootstrap: <library|docker|scratch|localimage|...>
From: <linux_distribution>:<version>
```

### %setup

Commands under `%setup` are executed on host OS after base container OS is
installed but before `%post`. This stage can be used for copying and extracting
program installers to a temporary location.

```
%setup
    # prepare installer
    rm -rf /tmp/installer
    mkdir -p /tmp/installer
    cp <package_installer.tar.gz> /tmp/installer
    cd /tmp/installer && tar -xzf /tmp/installer/<package_installer.tar.gz>
```

### %files

Files can be copied from host to container by specifying source path and
destination path in the container image. In singularity versions > 2.3, files
are copied before `%post`. In older versions, files are copied after `post`.

```
%files
    <source1_from_host> <destination1_in_container>
    <source2_from_host> <destination2_in_container>
```

### %post

Commands executed after base container OS installation for installing tools or
modifying container filesystem.

Unhandled commands that require user-interaction will generally timeout and
fail, so handle them accordingly by piping echo/printf statements.

```
%post
    # avoid package manager confirmation with -y flag
    apt-get install -y vim
    # Respond to installer input requests
    printf "y\ny\n" | /tmp/installer/package_installer
```

### %environment

Commands executed to configure environment variables during runtime.

```
%environment
    export LC_ALL=C
    export PATH=/opt/<vendor>/<tool>/bin:$PATH
```

## 3.2 Updating containers

TODO

Resources
=========

- https://sylabs.io/guides/3.7/user-guide/index.html
