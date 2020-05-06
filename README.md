# Introduction

Collection of scripts to set up OpenVINO environment

- Physical Device
- Containers

## Assumptions

- All instruction assumes you clone this repo to your home directory
- To make images smaller, I am using `experimental` feature  

    Enable `Experimental` feature by modifying `/etc/docker/daemon.json`  

    Create daemon.json if it does not exist

    ```json
    {
      "experimental": true
    }
    ```

## Physical Device Setup

This section covers how to setup OpenVINO Toolkit in silent mode.  
Once you set up your host machine, you can :

- Run OpenVINO application on the host machine
- Host containerized OpenVINO application (or container), including IoT Edge Module

This also covers setting up the host machine to run container

Currently tested with Ubuntu 16.04 nd 18.04 on UP2

- [Ubuntu 18.04 (Recommended)](Setup/Ubuntu/README.md)
- [Ubuntu 18.04 on UP2](Setup/UP2/README.md)
- [Raspbian (RP3 and RP4)](Setup/Raspbian/README.md)
- [Windows 10](Setup/Windows/README.md)

## Container Setup

This section covers multi-stage container build scripts and techniques.

Currently tested with Ubuntu 16.04 nd 18.04 on UP2

- [Ubuntu 18.04 (Recommended)](Container/README.md)
- Raspbian (RP3 and RP4) : To be added in the future
- Windows 10 : To be added in the future

### Motivation

Instead of building container from scratch, you can create `base image` and just add your application.

This saves time and disk space on your development machine.

