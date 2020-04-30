# Containerize the app

## Build a container with Python App

Build container with base image with :

- OpenVINO
- Python 3.7
- Ubuntu 18.04  (16.04 should work but have not tested yet)

Example :

./build-app-container.sh openvino-container:ubuntu18.04_openvino2020.2.120_cp3.7 myregistry

## Run the container

You need to run the container with several flags for GPU and Myriad Access

- GPU Access  
    `--device /dev/dri`
- VPU (Myriad) Access
    `--device-cgroup-rule='c 189:* rmw' -v /dev/bus/usb:/dev/bus/usb`

Example :

```bash
docker run -it --device-cgroup-rule='c 189:* rmw' -v /dev/bus/usb:/dev/bus/usb --device /dev/dri  -p 8080:8080 daisukeiot/openvino-container:ubuntu18.04_openvino2020.2.120_cp3.7_app
```

For UP2 (ATOM) :

```bash
docker run -it --device-cgroup-rule='c 189:* rmw' -v /dev/bus/usb:/dev/bus/usb --device /dev/dri  -p 8080:8080 daisukeiot/openvino-container:ubuntu18.04_openvino2020.2.120_r1.15_cp3.7_app
```


## Custom Tensorflow Build

ATOM Processors (e.g. UP2) do not support AVX, therefore, Tensorflow must be re-compiled without AVX support.

Make sure to use Tensorflow without AVX support, otherwise, Model Conversion and Inference won't work.
