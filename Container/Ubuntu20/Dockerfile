ARG TAG_BASE=ubuntu:20.04

FROM ${TAG_BASE} AS base

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

ARG OPENVINO_VER=2021.4.752
ENV DEBIAN_FRONTEND=noninteractive
ENV INTEL_OPENVINO_DIR /opt/intel/openvino

USER root
WORKDIR /

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

RUN echo "deb https://apt.repos.intel.com/openvino/2021 all main" | tee /etc/apt/sources.list.d/intel-openvino-2021.list && \
    apt-get update && \
#    apt-cache search intel-openvino-runtime-ubuntu20 && \
#    apt-cache search intel-openvino-dev-ubuntu20 && \
    apt-get install -y intel-openvino-dev-ubuntu20-${OPENVINO_VER}


WORKDIR /opt
RUN curl -L https://github.com/libusb/libusb/archive/v1.0.22.zip --output v1.0.22.zip && \
    unzip v1.0.22.zip

WORKDIR /opt/libusb-1.0.22
RUN ./bootstrap.sh && \
    ./configure --disable-udev --enable-shared && \
    make -j4

WORKDIR /opt/libusb-1.0.22/libusb
RUN /bin/mkdir -p '/usr/local/lib' && \
    /bin/bash ../libtool --mode=install /usr/bin/install -c   libusb-1.0.la '/usr/local/lib' && \
    /bin/mkdir -p '/usr/local/include/libusb-1.0' && \
    /usr/bin/install -c -m 644 libusb.h '/usr/local/include/libusb-1.0' && \
    /bin/mkdir -p '/usr/local/lib/pkgconfig'

WORKDIR /opt/libusb-1.0.22/
RUN /usr/bin/install -c -m 644 libusb-1.0.pc '/usr/local/lib/pkgconfig' && \
    cp /opt/intel/openvino_2021/deployment_tools/inference_engine/external/97-myriad-usbboot.rules /etc/udev/rules.d/ && \
    ldconfig

RUN apt-get update && \
    apt-get install -y sudo && \
    cd /opt/intel/openvino_2021/deployment_tools/demo/ && \
    ./demo_benchmark_app.sh -d CPU
