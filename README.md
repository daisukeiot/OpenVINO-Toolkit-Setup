# Introduction

Collection of scripts to set up OpenVINO environment

- Physical Device
- Containers

## Assumptions

- All instruction assumes you clone this repo to your home directory
  - ~/ on Linux
  - C:\ on Windows
- To make images smaller, all docker commands uses `--squash` experimental feature  

  Enable `Experimental` feature by modifying `/etc/docker/daemon.json`  

  Create daemon.json if it does not exist

  ```json
  {
    "experimental": true
  }
  ```

  > [!WARNING]  
  > --squash option did not work with Docker Desktop v19.03.8

## Physical Device Setup

These instructions cover how to setup OpenVINO Toolkit in silent mode, including libraries and tools.  
Once you set up your host machine, you can :

- Compile OpenVINO samples
- Develop OpenVINO Application
- Run OpenVINO application on the host machine
- Host containerized OpenVINO application (or container), including IoT Edge Module

Currently tested with following Operating Systems

- Ubuntu 18.04 on NUC (or Core iX CPU) : [Instruction](Setup/Ubuntu/README.md)
- Ubuntu 18.04 on UP Squared (UP2) : [Instruction](Setup/UP2/README.md)
- Windows 10 / Windows Server : [Instruction](Setup/Windows/README.md)
- Raspbian on Raspberry Pi 3 and Raspberry Pi 4 (Under test) : [Instruction](Setup/Raspbian/README.md) 

## Running Object Detection Python App

## Container Setup

This section covers multi-stage container build scripts and techniques.

Currently tested with Ubuntu 16.04 nd 18.04 on UP2

- [Ubuntu 18.04](Container/README.md)
- Raspbian (RP3 and RP4) : To be added in the future
- Windows 10 : To be added in the future

### Motivation

Instead of building container from scratch, you can create `base image` and just add your application.

This saves time and disk space on your development machine.

