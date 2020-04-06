#!/bin/bash

if [ $# -ne 1 ]
  then
    echo "======================================="
    echo "Please specify Container and Target Device"
    echo "  Example ./verify-container.sh myregistry/container:tag CPU"
    echo "======================================="
    exit
fi

#
# Build Container with verification script
# Built container but do not push to registry
#
TARGET_TAG=$1

#
# Build Container with verification script
# Built container but do not push to registry
#
./run-Verify-Container.sh $1 CPU
./run-Verify-Container.sh $1 GPU
./run-Verify-Container.sh $1 MYRIAD