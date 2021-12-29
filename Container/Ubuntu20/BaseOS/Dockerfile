#
# Ubuntu Version
#
ARG OS_VERSION=20.04

FROM ubuntu:${OS_VERSION}

#
# Run as root user
#
USER root
WORKDIR /tmp

ARG OPENVINO_VER=2021.4.752

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

ENV DEBIAN_FRONTEND=noninteractive

#
# Install libraries
#
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        tzdata \
        ca-certificates \
        autoconf \
        automake \
        build-essential \
        libtool \
        unzip \
        udev && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y gnupg && \
    curl https://apt.repos.intel.com/openvino/2021/GPG-PUB-KEY-INTEL-OPENVINO-2021 > ./intel-key && \
    apt-key add ./intel-key

WORKDIR /opt
RUN curl -L https://github.com/libusb/libusb/archive/v1.0.22.zip --output v1.0.22.zip && \
    unzip v1.0.22.zip && \
    rm -rf v1.0.22.zip

WORKDIR /opt/libusb-1.0.22
RUN ./bootstrap.sh && \
    ./configure --disable-udev --enable-shared && \
    make -j4

ENTRYPOINT []
