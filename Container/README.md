# Docker Container with OpenVINO

There are a few steps involved in containerize OpenVINO application

Create a container with :

1. Ubuntu OS
1. Install OpenVINO Toolkit
1. Install drivers/libraries
1. Install your app

Since it takes time to build container from scratch, I created a few scripts to build OpenVINO container in multi-stage way.

This involves:

1. Base OS Container (BaseOS)
1. OpenVINO Toolkit installed to `BaseOS` (OpenVINOToolKit)
1. Your app installed to `OpenVINOToolKit`

Once you have `OpenVINOToolKit` container, you can just install your app instead of building the container from scratch every time.

Let's get tactical (-:

## Use pre-built containers

You may use container image from my registry

- If you just want to add your app, then you can `OpenVINOToolKit` container as your base image (FROM line)
- If you would like to change some settings, you can still use `BaseOS` container and customize `Dockerfile-OpenVINO-ToolKit`

> [!IMPORTANT]  
> You may need to build your own CPU Extension library for your CPU

|Tag                                          | OS           | OpenVINO Toolkit |Size (MB) |
|---------------------------------------------|--------------|------------------|----------|
|daisukeiot/openvino-toolkit:16.04_2019.3.376 | Ubuntu 16.04 | 2019.3.376       |625.99    |
|daisukeiot/openvino-toolkit:18.04_2019.3.376 | Ubuntu 18.04 | 2019.3.376       |          |

## Build your own containers

Follow instructions below to build containers

1. Build `BaseOS` container
1. Build `OpenVINOToolKit` container by installing OpenVINO Toolkit to `BaseOS` container
1. Build your own container with your OpenVINO application to `OpenVINOToolKit` container

## Build OS Base Image (#1)

Builds a container with :

- Ubuntu OS
- A new user `openvino`
- Add `openvino` user to Video Group to access GPU
- Install Libraries
- Install the latest Intel libraries for Ubuntu 18.04  
    They have dependencies on libc version etc so skipping this for Ubuntu 16.04

> [!CAUTION]  
> Make sure to log in to your registry before you push image  
> docker login -u `<user>` -p `<password>` `<registry>`

```bash
export MY_REGISTRY=<Your Registry>
export UBUNTU_VER=<Ubuntu Version>
cd ~/OpenVINO-Toolkit-Setup/Container
docker build --squash --rm -f ./dockerfile/Dockerfile-Ubuntu${UBUNTU_VER} -t ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER} .
docker push ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER}
```

Example :

- User `myrepo` docker hub registry
- Use Ubuntu 18.04

```bash
export MY_REGISTRY=myrepo
export UBUNTU_VER=18.04
cd ~/OpenVINO-Toolkit-Setup/Container
docker build --squash --rm -f ./dockerfile/Dockerfile-Ubuntu${UBUNTU_VER} -t ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER} .
docker push ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER}
```

or run `build-BaseOS.sh` script to built both Ubuntu 16.04 and 18.04

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
./build-BaseOS.sh
```

This will create container with Ubuntu + libraries

|Tag                                    | OS           | Size (MB) | Notes               |
|---------------------------------------|--------------|-----------|---------------------|
|openvino-toolkit:baseos-ubuntu_16.04   | Ubuntu 16.04 | 577       |                     |
|openvino-toolkit:baseos-ubuntu_18.04   | Ubuntu 18.04 | 581       | With [Latest Intel OpenCL](https://github.com/intel/compute-runtime) |

### Verify Base OS Container

Run quick sanity check with :

```bash
export MY_REGISTRY=<Your Registry>
export UBUNTU_VER=<Ubuntu Version>
cd ~/OpenVINO-Toolkit-Setup/Container
docker run -it --rm ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER} /bin/bash -c "python3 --version;lsb_release -a"
```

Example :

- User `myrepo` docker hub registry
- Use Ubuntu 18.04

```bash
export MY_REGISTRY=myrepo
export UBUNTU_VER=18.04
cd ~/OpenVINO-Toolkit-Setup/Container
docker run -it --rm ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER} /bin/bash -c "python3 --version;lsb_release -a"
```

This should show :

- Python version
- Ubuntu OS Version information from `lsb_release` command

Example Output :

```bash
Python 3.6.9
No LSB modules are available.
Distributor ID: Ubuntu
Description:    Ubuntu 18.04.4 LTS
Release:        18.04
Codename:       bionic
```

## Build OpenVINO Base image (#2)

Builds a container with :

- Using `Base OS Image` (#1)
- Install OpenVINO Toolkit

```bash
export MY_REGISTRY=<Your Registry>
export UBUNTU_VER=<Ubuntu Version>
export OPENVINO_VER=<OpenVINO Toolkit Version>
cd ~/OpenVINO-Toolkit-Setup/Container
docker build --squash --rm -f ./dockerfile/Dockerfile-OpenVINO-Toolkit -t ${MY_REGISTRY}/openvino-ubuntu${UBUNTU_VER}:${OPENVINO_VER} --build-arg UBUNTU_VER=${UBUNTU_VER} --build-arg docker push ${MY_REGISTRY}/openvino-ubuntu${UBUNTU_VER}:${OPENVINO_VER}
```

Example :

- User `myrepo` docker hub registry
- Use Ubuntu 18.04
- Use OpenVINO Toolkit ver 2019.3.376

```bash
export MY_REGISTRY=myrepo
export OPENVINO_VER=2019.3.376
export UBUNTU_VER=18.04
cd ~/OpenVINO-Toolkit-Setup/Container
docker build --squash --rm -f ./dockerfile/Dockerfile-OpenVINO-Toolkit -t ${MY_REGISTRY}/openvino-ubuntu${UBUNTU_VER}:${OPENVINO_VER} --build-arg UBUNTU_VER=${UBUNTU_VER} --build-arg OPENVINO_VER=${OPENVINO_VER} .
docker push ${MY_REGISTRY}/openvino-ubuntu${UBUNTU_VER}:${OPENVINO_VER}
```

or run `OpenVINO-Toolkit.sh` script to built both Ubuntu 16.04 and 18.04

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
./build-OpenVINO-Toolkit.sh
```

This will create container with Ubuntu + libraries

|Tag                               | OS           | OpenVINO Toolkit |Size (GB) | Notes    |
|----------------------------------|--------------|------------------|----------|----------|
|openvino-toolkit:16.04_2019.3.376 | Ubuntu 16.04 | 2019.3.376       |1.57      |          |
|openvino-toolkit:18.04_2019.3.376 | Ubuntu 18.04 | 2019.3.376       |    |          |

https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_docker_linux.html

### Verify OpenVINO Toolkit Container

#### Build a container with Verification Script

Verify container using verification script provided by OpenVINO Toolkit by adding script to `OpenVINO Base image` (#2).
This adds `verify.sh` to `/home/openvino` and `sudo` command.

> [!WARNING]  
> This has to be run on a machine with Intel CPU, Movidius/Myriad X with OpenVINO Toolkit installed on the host machine.
> Please see [Physical Device Setup (UP2)](#physical-device-setup-up2)

Run Verification script with :

```bash
export MY_REGISTRY=<Your Registry>
export UBUNTU_VER=<Ubuntu Version>
export OPENVINO_VER=<OpenVINO Toolkit Version>
cd ~/OpenVINO-Toolkit-Setup/Container
docker build --squash --rm -f ./dockerfile/Dockerfile-OpenVINO-Toolkit-Verification -t ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify --build-arg UBUNTU_VER=${UBUNTU_VER} --build-arg OPENVINO_VER=${OPENVINO_VER} .
```

Example :

- User `myrepo` docker hub registry
- Use Ubuntu 18.04
- Use OpenVINO Toolkit ver 2019.3.376

```bash
export MY_REGISTRY=myrepo
export OPENVINO_VER=2019.3.376
export UBUNTU_VER=18.04
cd ~/OpenVINO-Toolkit-Setup/Container
docker build --squash --rm -f ./dockerfile/Dockerfile-OpenVINO-Toolkit-Verification -t ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify --build-arg UBUNTU_VER=${UBUNTU_VER} --build-arg OPENVINO_VER=${OPENVINO_VER} .
```

or run `build-verify-container.sh` script to built both Ubuntu 16.04 and 18.04

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
./build-verify-container.sh
```

#### Run Verification Script in the Container

```bash
export MY_REGISTRY=<Your Registry>
export UBUNTU_VER=<Ubuntu Version>
export OPENVINO_VER=<OpenVINO Toolkit Version>
cd ~/OpenVINO-Toolkit-Setup/Container
docker run --rm -it -e "TARGET=CPU" ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify
docker run --rm -it -e "TARGET=GPU" --device /dev/dri ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify
docker run --rm -it -e "TARGET=MYRIAD" --privileged -v /dev:/dev ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify
```

Example :

- User `myrepo` docker hub registry
- Use Ubuntu 18.04
- Use OpenVINO Toolkit ver 2019.3.376

```bash
export MY_REGISTRY=myrepo
export OPENVINO_VER=2019.3.376
export UBUNTU_VER=18.04
cd ~/OpenVINO-Toolkit-Setup/Container
docker run --rm -it -e "TARGET=CPU" ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify
docker run --rm -it -e "TARGET=GPU" --device /dev/dri ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify
docker run --rm -it -e "TARGET=MYRIAD" --privileged -v /dev:/dev ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify
```

or run `verify-container.sh` to run the Verification script for both Ubuntu 16.04 and 18.04 with all targets

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
./verify-container.sh
```
