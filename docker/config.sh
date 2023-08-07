# shellcheck shell=bash

PROJECT_DIR=$(dirname "$SCRIPT_DIR")
TVM_DIR="$PROJECT_DIR"/compilers/tvm-main
GLOW_DIR="$PROJECT_DIR"/compilers/glow-main
NNFUSION_DIR="$PROJECT_DIR"/compilers/nnfusion-main
RESOURCES_DIR="$PROJECT_DIR"/resources

BASE_IMAGE=cnly/dotfiles-full:bullseye-20230109-c20df35
BUILT_IMAGE=debfa-runner
