Singularity Container Tutorial
==============================

Written and maintained by Hansem Ro (`hansemro@outlook.com`).

This tutorial covers the following topics:

0. [ ] Singularity Purpose
1. [ ] Container usage (on work node)
    - 1.1 [ ] Bind Paths
2. [ ] Container instances
    - 2.1 [ ] Starting/stopping instance
    - 2.2 [ ] Checking instance(s)
    - 2.3 [ ] Entering instance
3. [ ] Building containers
    - 3.1 [ ] General guidance for writing container recipes
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

TODO

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

# 3. Building containers from scratch

TODO

## 3.1 General guidance for writing container recipes

Because Singularity does not allow any interaction during the building process,
everything step in the recipe cannot require human-intervention. This requires
the container developer to automate every step that a human may do.

### Header
### %setup
### %files
### %post
### %environment
### %help

## 3.2 Updating containers

TODO

Resources
=========

- https://sylabs.io/guides/3.7/user-guide/index.html
