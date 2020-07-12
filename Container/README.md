# Docker Container with OpenVINO for Ubuntu

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
- If you would like to change some settings, you can still use `BaseOS` image and customize `Dockerfile.OpenVINO-ToolKit`

> [!IMPORTANT]  
> You may need to build your own CPU Extension library for your CPU

| Tag                                            | OS           | OpenVINO Toolkit | Size (MB) |
|------------------------------------------------|--------------|------------------|-----------|
| daisukeiot/openvino-container:16.04_2020.3.194 | Ubuntu 16.04 | 2020.3.194       |           |
| daisukeiot/openvino-container:18.04_2020.3.194 | Ubuntu 18.04 | 2020.3.194       |           |

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

### Build Base OS Container with script

Run `./Ubuntu/build-BaseOS.sh` to build a Base OS image with :

```bash
cd ~/OpenVINO-Toolkit-Setup/Container/Ubuntu
./build-BaseOS.sh <Ubuntu Version> <Container Registry>
```

#### Script Parameters

- Ubuntu Version  
  Currently verified with 16.04 and 18.04

- Container Registry
  Your Container Registry

### Manually Build Base OS Container

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
export OS_VERSION=<Ubuntu Version.  18.04 or 16.04>
export MY_REGISTRY=<Container Registry>
export TAG=${MY_REGISTRY}/openvino-container:baseos-ubuntu_${OS_VERSION}

docker build --squash --rm -f ./Ubuntu/BaseOS/Dockerfile --build-arg OS_VERSION=${OS_VERSION} -t ${TAG} .
docker push ${TAG}
```

Example :

- Push to `myregistry` docker hub container registry
- Use Ubuntu 18.04

```bash
cd ~/OpenVINO-Toolkit-Setup/Container

export MY_REGISTRY=myregistry
export OS_VERSION=18.04
export TAG=${MY_REGISTRY}/openvino-container:baseos-ubuntu_${OS_VERSION}

docker build --squash --rm -f ./Ubuntu/BaseOS/Dockerfile --build-arg OS_VERSION=${OS_VERSION} -t ${TAG} .
docker push ${TAG}
```

This will create container with Ubuntu + libraries

| Tag                 | OS           | Size (MB) | Notes                                                                |
|---------------------|--------------|-----------|----------------------------------------------------------------------|
| baseos-ubuntu_16.04 | Ubuntu 16.04 | 577       |                                                                      |
| baseos-ubuntu_18.04 | Ubuntu 18.04 | 581       | With [Latest Intel OpenCL](https://github.com/intel/compute-runtime) |

Example :

<myregistry/openvino-container:baseos-ubuntu_16.04>

### Verify `BaseOS` Image

Run quick sanity check with :

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
export MY_REGISTRY=<Container Registry>
export OS_VERSION=<Ubuntu Version>
export TAG=${MY_REGISTRY}/openvino-container:baseos-ubuntu_${OS_VERSION}

docker run -it --rm ${TAG} /bin/bash -c "python3 --version;lsb_release -a"
```

Example :

- Use `myregistry` docker hub registry
- Use Ubuntu 18.04

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
export MY_REGISTRY=myregistry
export OS_VERSION=18.04
export TAG=${MY_REGISTRY}/openvino-container:baseos-ubuntu_${OS_VERSION}

docker run -it --rm ${TAG} /bin/bash -c "python3 --version;lsb_release -a"
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

- Use `Base OS Image` (#1) as a base image
- Install OpenVINO Toolkit

> [!IMPORTANT]  
> Instructions below assumes you have Base OS containers from above

### Build OpenVINO Container with script

Run `./Ubuntu/build-OpenVINO-Toolkit.sh` to build a Base OS image with :

```bash
cd ~/OpenVINO-Toolkit-Setup/Container/Ubuntu
./build-OpenVINO-Toolkit.sh <Ubuntu Version> <Container Registry>
```

### Manually Build OpenVINO Container

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
export OPENVINO_VER=2020.3.194
export MY_REGISTRY=<Your Registry>
export OS_VERSION=<Ubuntu Version>
export TAG=${MY_REGISTRY}/openvino-container:ubuntu${OS_VERSION}_openvino${OPENVINO_VER}

docker build --squash --rm -f ./Ubuntu/OpenVINO-Toolkit/Dockerfile -t ${TAG} \
  --build-arg OS_VERSION=${OS_VERSION} \
  --build-arg OPENVINO_VER=${OPENVINO_VER} \
  --build-arg MY_REGISTRY=${MY_REGISTRY} .

docker push ${TAG}
```

Example :

- Push to `myregistry` docker hub container registry
- Use OpenVINO Toolkit ver 2020.3.194
- Use Ubuntu 18.04

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
export OPENVINO_VER=2020.3.194
export MY_REGISTRY=myregistry
export OS_VERSION=18.04
export TAG=${MY_REGISTRY}/openvino-container:ubuntu${OS_VERSION}_openvino${OPENVINO_VER}

docker build --squash --rm -f ./Ubuntu/OpenVINO-Toolkit/Dockerfile -t ${TAG} \
  --build-arg OS_VERSION=${OS_VERSION} \
  --build-arg OPENVINO_VER=${OPENVINO_VER} \
  --build-arg MY_REGISTRY=${MY_REGISTRY} .

docker push ${TAG}
```

This will create a container image with Ubuntu + OpenVINO Toolkit

| Tag                            | OS    | OpenVINO Toolkit | Size    | Notes |
|--------------------------------|-------|------------------|---------|-------|
| ubuntu16.04_openvino2020.3.194 | 16.04 | 2020.3.194       | 1.57 GB |       |
| ubuntu18.04_openvino2020.3.194 | 18.04 | 2020.3.194       | 1.68 GB |       |

### Reference

<https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_docker_linux.html>

## Verify `OpenVINOToolKit` image

In order to verify the image can run OpenVINO application on different hardware target (CPU, GPU, and/or MYRIAD/VPU), let's build another image with `Sample/Demo` app and `Benchmark` app from OpenVINO Toolkit.

<https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_linux.html#run-the-demos>

### Build a container with demo apps with a script

Run `./Ubuntu/build-OpenVINO-Toolkit.sh` to build a Base OS image with :

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
./build-Verify-Container.sh <OpenVINO Container>
```

Example :

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
./build-Verify-Container.sh myregistry/openvino-container:ubuntu18.04_openvino2020.3.194
```

### Manually build a container image with demo apps

Build a new image by adding sample/demo app to `OpenVINOToolKit` image (#2).

`Dockerfile.OpenVINO-Tooolkit-Verification` adds :

- `imageclassification.sh` and `benchmark.sh` to `/home/openvino`
- `sudo` command

> [!WARNING]  
> This has to be run on a machine with Intel CPU, Movidius/Myriad X with OpenVINO Toolkit installed on the host machine.
> Please see [Physical Device Setup (UP2)](#physical-device-setup-up2)

Run Verification script with :

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
export TAG=<OpenVINO Container built above>
export TAG_VERIFY=<New Tag for verification>

docker build --squash --rm -f ./Common/Classification-Demo_Benchmark/Dockerfile \
    -t ${TAG_VERIFY} \
    --build-arg OPENVINO_IMAGE=${TAG} \
    ./Common/Classification-Demo_Benchmark
```

Example :

- Use `ubuntu18.04_openvino2020.3.194`
- Use `ubuntu18.04_openvino2020.3.194_verify` for the new image

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
export TAG=myregistry/openvino-container:ubuntu18.04_openvino2020.3.194
export TAG_VERIFY=${TAG}_verify

docker build --squash --rm -f ./Common/Classification-Demo_Benchmark/Dockerfile \
    -t ${TAG_VERIFY} \
    --build-arg OPENVINO_IMAGE=${TAG} \
    ./Common/Classification-Demo_Benchmark
```

### Check Available Hardware devices

Run python script in the container to check available hardware devices with :

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
export TAG=<OpenVINO Container built above>
export TAG_VERIFY=<New Tag for verification>

docker run --rm -it --privileged -v /dev:/dev --network=host ${TAG_VERIFY} /home/openvino/hello_device.sh
```

### Run Verification Script in the Container

The new container contains `imageclassification.sh` and `benchmark.sh` in `/home/openvino/` folder.

- imageclassification.sh  
  Runs [Image Classification Sample](https://docs.openvinotoolkit.org/latest/_inference_engine_samples_classification_sample_async_README.html)

- benchmark.sh  
  Runs [Benchmark C++ Tool](https://docs.openvinotoolkit.org/latest/_inference_engine_samples_benchmark_app_README.html)

You may run these tools against CPU, GPU, or Myriad.

Specify the target device with `TARGET` environment variable or as a parameter for these scrips

Run `imageclassification.sh` agains CPU with :

#### Examples

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
export TAG=myregistry/openvino-container:ubuntu18.04_openvino2020.3.194
export TAG_VERIFY=${TAG}_verify
docker run --rm -it -e "TARGET=CPU" ${TAG_VERIFY} /home/openvino/imageclassification.sh
```

Run 'benchmark.sh` against GPU with :

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
export TAG=myregistry/openvino-container:ubuntu18.04_openvino2020.3.194
export TAG_VERIFY=${TAG}_verify
docker run --rm -it -e "TARGET=GPU" ${TAG_VERIFY} /home/openvino/benchmark.sh
```

Run `benchmark.sh` against Myriad with :

```bash
cd ~/OpenVINO-Toolkit-Setup/Container
export TAG=myregistry/openvino-container:ubuntu18.04_openvino2020.3.194
export TAG_VERIFY=${TAG}_verify
docker run --rm -it ${TAG_VERIFY} /home/openvino/benchmark.sh MYRIAD
```

### Sample Output from Benchmark Tool

On UP2 + Myriad X

```bash
CPU
Count:      1276 iterations
Duration:   60172.85 ms
Latency:    182.87 ms
Throughput: 21.21 FPS

GPU
Count:      3136 iterations
Duration:   60094.18 ms
Latency:    76.45 ms
Throughput: 52.18 FPS

MyriadX
Count:      3628 iterations
Duration:   60078.82 ms
Latency:    66.17 ms
Throughput: 60.39 FPS
```
