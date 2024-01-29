# DEBFA (DNN Executables Bitflip Attacks)

## Overview

This is the research artifact for the paper *Compiled Models, Built-In
Exploits: Uncovering Pervasive Bit-Flip Attack Surfaces in DNN Executables*.
It contains the code, data, and results for the paper and also enables future
research on the topic.

Note: Currently our data (close to 100GB, including model weights, compiled
binaries, analysis results, etc.) is stored on an internal server and not
publicly accessible.
We will clean up the data and upload it to a public storage service once the
paper is accepted.

## Getting Started

### Setting Up

These external dependencies are needed for this project:

* [Pyenv](https://github.com/pyenv/pyenv#getting-pyenv)
* Docker

For the remaining dependencies, the first-time setup script will install them
automatically.
You also need to ensure you can ssh to `<redacted for review>` without password in order to
pull the larger data files stored with DVC (free disk space of 200GB is
recommended). To do this, you can create a key pair and copy the public key to
the server with

```sh
ssh-keygen -b 4096
ssh-copy-id <redacted for review>
```

Clone this repo and run the first-time setup script:

```sh
cd debfa
./setup.sh
```

This script will

* Initialise all git submodules including the DL compilers
* Use Pyenv to install Python 3.8.12 and install the dependencies in the
  virtual environment `venv/`
* Pull data files from `<redacted for review>` using DVC
* Build a Docker image `debfa-runner` so later tasks can be run in a stable
  and reproducible environment

### Noteworthy Notes

Remember to

```sh
source env.sh
```

before working on the project.

This project contains large files git is not good at tracking, e.g. datasets
and built binaries. They are tracked using [DVC](https://dvc.org/) which
should've been installed in the virtual environment. Every time new commits are
pulled, remember to run

```sh
dvc pull
```

as well to pull any new or modified data from `<redacted for review>`. Note that if you
have new or modified files in folders like `built/`, `datasets/`, or
`results/sweep/`, this command may **delete/overwrite** them!

To use the Docker image built earlier, run

```sh
docker/run-in-docker.sh <command>
```

## Usage

### Adding New Datasets

Usually dataset files live in `datasets/`, as configured in `cfg.py`. If your
new dataset is too large, you may consider symlinking it from somewhere else,
or modifying the config.

Once your dataset is ready, you may need to edit `dataman.py` to expose it.

### Training Models

The definitions of models are in `support/models/`. To obtain the weights for a
model, you may train somewhere else and move the weights `.pt` file to
`models/<dataset>/<modelname>/<modelname>.pt`. Alternatively, you can use the
training script `support/models/train.py`.

### Building and Analysing the Binary

After training, you can add the new model(s) to the build combinations in
`cfg.py`, and then run

```sh
dvc repro
```

which should build the binaries, import them into Ghidra, and generate the
sweep range information for later use.

Note that if you want to rebuild and/or redo the analysis done on a binary, you
need to **manually delete the existing files for them**. For the former you
just need to `rm` the files, but for the latter you may need to do it in Ghidra
GUI. Alternatively, you can discard the changes and restore them by running

```sh
git checkout -- dvc.lock
dvc checkout
```

### Sweeping for Vulnerable Bits

Use `flipsweep.py` to brute force through all bits in compute functions and
look for vulnerable ones. For example, run

```sh
docker/run-in-docker.sh ./flipsweep.py -m resnet50 -d CIFAR10 MNISTC FashionC -a 50
```

to look for superbits in three ResNet50 models trained on CIFAR10, MNISTC, and
FashionC, respectively. The `-a` option speeds up the sweep by specifying the
accuracy threshold, i.e. if the accuracy of any model after flipping a bit is
still above this threshold, the bit won't be considered vulnerable or further
assessed for the remaining models.

This process can take a long time, but you can safely interrupt by pressing
`^C` twice. The resulting file is saved in `results/sweep/`. Note that if you
run `dvc checkout` later, the new file may get **deleted**.

### Obtaining DRAM Profiles

A sweep summary JSON produced by
[Blacksmith](https://github.com/comsec-group/blacksmith) is required to be
placed in `results/dram/` for the Rowhammer attack experiment later.
For instructions to run Blacksmith, please follow the README in its repo.
To reduce the noise in the output of Blacksmith's timing function, you can also
replace it with the one from [TRRespass](https://github.com/vusec/trrespass).

### Reproducing Experiments

Once prior steps are done, you can reproduce the experiments in the paper by
running

```sh
dvc repro
```

which will run the basic analysis, find superbits, and perform the practical
Rowhammer experiments.
The results will be available in `results/`. Note that if you run `dvc
checkout` later, the new files may get **deleted**.
