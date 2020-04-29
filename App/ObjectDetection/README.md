# Containerize the app

## Build a conatiner with Python App

Build container with base image with :

- OpenVINO
- Python 3.7
- Ubuntu 18.04  (16.04 should work but have not tested yet)

Example :

./build-app-container.sh openvino-container:ubuntu18.04_openvino2020.2.120_cp3.7 myregistry

## Run the container

You need to run the container with :

- Access to GPU and/or Myriad you need --priviledged flag
- To access Myriad, you need to --network=host

docker run -it --rm --privileged -v /dev:/dev --network=host myregistry/openvino-container:ubuntu18.04_openvino2020.2.120_cp3.7_app

## Custom Tensorflow Build

ATOM Processors (e.g. UP2) do not support AVX, therefore, Tensorflow must be re-compiled without AVX support.

Make sure to use Tensorflow without AVX support, otherwise, Model Conversion and Inference won't work