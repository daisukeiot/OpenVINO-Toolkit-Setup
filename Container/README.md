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

Once you have `OpenVINOToolKit` container, you can just install your app instead of building the images from scratch every time.

Let's get tactical (-:

## Use pre-built images

You may use pre-built images from my registry

- If you just want to add your app, then you can `OpenVINOToolKit` image as your base image (FROM line)
- If you would like to change some settings, you can still use `BaseOS` image and customize `Dockerfile-OpenVINO-ToolKit`

> [!IMPORTANT]  
> You may need to build your own CPU Extension library for your CPU

|Tag                                          | OS           | OpenVINO Toolkit |Size (MB) |
|---------------------------------------------|--------------|------------------|----------|
|daisukeiot/openvino-toolkit:16.04_2019.3.376 | Ubuntu 16.04 | 2019.3.376       |    |
|daisukeiot/openvino-toolkit:18.04_2019.3.376 | Ubuntu 18.04 | 2019.3.376       |          |

## Build your own images

Follow instructions below to build images

1. Build `BaseOS` image
1. Build `OpenVINOToolKit` image by installing OpenVINO Toolkit to `BaseOS` image
1. Build your own image by installing your OpenVINO application to `OpenVINOToolKit` image

## Build `BaseOS` Image (#1)

Builds a container image with :

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
docker build --squash --rm -f ./dockerfile/Dockerfile-Ubuntu --build-arg UBUNTU_VER=${UBUNTU_VER} -t ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER} .
docker push ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER}
```

Example :

- Push to `myregistry` docker hub container registry
- Use Ubuntu 18.04

```bash
export MY_REGISTRY=myregistry
export UBUNTU_VER=18.04
cd ~/OpenVINO-Toolkit-Setup/Container
docker build --squash --rm -f ./dockerfile/Dockerfile-Ubuntu --build-arg UBUNTU_VER=${UBUNTU_VER} -t ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER} .
docker push ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER}
```

or run `build-BaseOS.sh` script to built `Base OS` container image

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
./build-BaseOS.sh 16.04 [your registry]
./build-BaseOS.sh 18.04 [your registry]
```

This will create container with Ubuntu + libraries

|Tag                                    | OS           | Size (MB) | Notes               |
|---------------------------------------|--------------|-----------|---------------------|
|openvino-toolkit:baseos-ubuntu_16.04   | Ubuntu 16.04 | 577       |                     |
|openvino-toolkit:baseos-ubuntu_18.04   | Ubuntu 18.04 | 581       | With [Latest Intel OpenCL](https://github.com/intel/compute-runtime) |

### Verify `BaseOS` Image

Run quick sanity check with :

```bash
export MY_REGISTRY=<Your Registry>
export UBUNTU_VER=<Ubuntu Version>
cd ~/OpenVINO-Toolkit-Setup/Container
docker run -it --rm ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER} /bin/bash -c "python3 --version;lsb_release -a"
```

Example :

- Use `myregistry` docker hub registry
- Use Ubuntu 18.04

```bash
export MY_REGISTRY=myregistry
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

## Build `OpenVINOToolKit` image (#2)

Builds a container image with :

- From `Base OS Image` (#1)
- Install OpenVINO Toolkit
- Push to container registry

```bash
export MY_REGISTRY=<Your Registry>
export UBUNTU_VER=<Ubuntu Version>
export OPENVINO_VER=<OpenVINO Toolkit Version>
cd ~/OpenVINO-Toolkit-Setup/Container
docker build --squash --rm -f ./dockerfile/Dockerfile-OpenVINO-Toolkit -t ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER} --build-arg UBUNTU_VER=${UBUNTU_VER} --build-arg OPENVINO_VER=${OPENVINO_VER} --build-arg MY_REGISTRY=${MY_REGISTRY} .
docker push ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}
```

Example :

- Push to `myregistry` docker hub container registry
- Use OpenVINO Toolkit ver 2019.3.376
- Use Ubuntu 18.04

```bash
export MY_REGISTRY=myregistry
export OPENVINO_VER=2019.3.376
export UBUNTU_VER=18.04
cd ~/OpenVINO-Toolkit-Setup/Container
docker build --squash --rm -f ./dockerfile/Dockerfile-OpenVINO-Toolkit -t ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER} --build-arg UBUNTU_VER=${UBUNTU_VER} --build-arg OPENVINO_VER=${OPENVINO_VER} --build-arg MY_REGISTRY=${MY_REGISTRY} .
docker push ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}
```

or run `build-OpenVINO-Toolkit.sh` script to built both Ubuntu 16.04 and 18.04

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
./build-OpenVINO-Toolkit.sh 16.04 [Your Registry]
./build-OpenVINO-Toolkit.sh 18.04 [Your Registry]
```

This will create a container image with Ubuntu + OpenVINO Toolkit

|Tag                               | OS           | OpenVINO Toolkit |Size (GB) | Notes    |
|----------------------------------|--------------|------------------|----------|----------|
|openvino-toolkit:16.04_2019.3.376 | Ubuntu 16.04 | 2019.3.376       |1.57      |          |
|openvino-toolkit:18.04_2019.3.376 | Ubuntu 18.04 | 2019.3.376       |1.68      |          |

### Reference

<https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_docker_linux.html>

## Verify `OpenVINOToolKit` image

In order to verify the image can run OpenVINO application on different hardware target (CPU, GPU, and/or MYRIAD/VPU), let's build another image with `Sample/Demo` app and `Benchmark` app from OpenVINO Toolkit.

<https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_linux.html#run-the-demos>

### Build an image with demo apps

Build a new image by adding sample/demo app to `OpenVINOToolKit` image (#2).

`Dockerfile-OpenVINO-Tooolkit-Verification` adds :

- `verify.sh` and `benchmark.sh` to `/home/openvino`
- `sudo` command

> [!WARNING]  
> This has to be run on a machine with Intel CPU, Movidius/Myriad X with OpenVINO Toolkit installed on the host machine.
> Please see [Physical Device Setup (UP2)](#physical-device-setup-up2)

Run Verification script with :

```bash
export MY_REGISTRY=<Your Registry>
export UBUNTU_VER=<Ubuntu Version>
export OPENVINO_VER=<OpenVINO Toolkit Version>
cd ~/OpenVINO-Toolkit-Setup/Container
docker build --squash --rm -f ./dockerfile/Dockerfile-OpenVINO-Toolkit-Verification -t ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify --build-arg UBUNTU_VER=${UBUNTU_VER} --build-arg OPENVINO_VER=${OPENVINO_VER} --build-arg MY_REGISTRY=${MY_REGISTRY} .
```

Example :

- User `myregistry` docker hub registry
- Use Ubuntu 18.04
- Use OpenVINO Toolkit ver 2019.3.376

```bash
export MY_REGISTRY=myregistry
export OPENVINO_VER=2019.3.376
export UBUNTU_VER=18.04
cd ~/OpenVINO-Toolkit-Setup/Container
docker build --squash --rm -f ./dockerfile/Dockerfile-OpenVINO-Toolkit-Verification -t ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify --build-arg UBUNTU_VER=${UBUNTU_VER} --build-arg OPENVINO_VER=${OPENVINO_VER} --build-arg MY_REGISTRY=${MY_REGISTRY} .
```

or run `build-verify-container.sh` script to built both Ubuntu 16.04 and 18.04

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
./build-verify-container.sh 16.04 [your registry]
./build-verify-container.sh 18.04 [your registry]
```

### Run Verification Script in the Container

- Run `verify.sh` to run [Image Classification Sample](https://docs.openvinotoolkit.org/latest/_inference_engine_samples_classification_sample_async_README.html)

- Run `benchmark.sh` to run [Benchmark C++ Tool](https://docs.openvinotoolkit.org/latest/_inference_engine_samples_benchmark_app_README.html)

```bash
export MY_REGISTRY=<Your Registry>
export UBUNTU_VER=<Ubuntu Version>
export OPENVINO_VER=<OpenVINO Toolkit Version>
cd ~/OpenVINO-Toolkit-Setup/Container
docker run --rm -it -e "TARGET=CPU" ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify /home/openvino/verify.sh
docker run --rm -it -e "TARGET=GPU" --device /dev/dri ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify /home/openvino/verify.sh
docker run --rm -it -e "TARGET=MYRIAD" --privileged -v /dev:/dev ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify /home/openvino/verify.sh
```

Example :

- User `myregistry` docker hub registry
- Use Ubuntu 18.04
- Use OpenVINO Toolkit ver 2019.3.376

```bash
export MY_REGISTRY=myregistry
export OPENVINO_VER=2019.3.376
export UBUNTU_VER=18.04
cd ~/OpenVINO-Toolkit-Setup/Container
docker run --rm -it -e "TARGET=CPU" ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify
docker run --rm -it -e "TARGET=GPU" --device /dev/dri ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify
docker run --rm -it -e "TARGET=MYRIAD" --privileged -v /dev:/dev ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify
```

### Run Benchmark App

Verification Container is built with Benchmark app as well.  

To run Benchmark App :

```bash
export MY_REGISTRY=<Your Registry>
export UBUNTU_VER=<Ubuntu Version>
export OPENVINO_VER=<OpenVINO Toolkit Version>
cd ~/OpenVINO-Toolkit-Setup/Container
docker run --rm -it -e "TARGET=CPU" ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify /home/openvino/benchmark.sh
docker run --rm -it -e "TARGET=GPU" --device /dev/dri ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify /home/openvino/benchmark.sh
docker run --rm -it -e "TARGET=MYRIAD" --privileged -v /dev:/dev ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify /home/openvino/benchmark.sh
```

or run `verify-container.sh` to run the Verification script for both Ubuntu 16.04 and 18.04 with all targets

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
./verify-container.sh
```

