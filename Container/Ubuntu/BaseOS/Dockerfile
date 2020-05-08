#
# Ubuntu Version
#
ARG OS_VERSION=18.04
FROM ubuntu:${OS_VERSION}

ARG OS_VERSION=18.04

ENV PYTHON_VERSION=3.7
ARG PYTHON_BIN=python${PYTHON_VERSION}

#
# Run as root user
#
USER root
WORKDIR /tmp

#
# Create user `openvino`
#
RUN useradd -ms /bin/bash openvino && \
    chown openvino -R /home/openvino

#
# Install libraries
#
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                autoconf \
                automake \
                build-essential \
                cmake \
                cpio \
                curl \
                gnupg2 \
                libdrm2 \
                libglib2.0-0 \
                lsb-release \
                libgtk-3-0 \
                libtool \
                ${PYTHON_BIN} \
                ${PYTHON_BIN}-dev \
                python3-pip \
                udev \
                unzip \
                ocl-icd-libopencl1 \
                python3-setuptools \
                libpython3-dev \
                python3-wheel && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3 get-pip.py && \
    ${PYTHON_BIN} get-pip.py && \
    cd /usr/lib/python3/dist-packages && \
    ln -s apt_pkg.cpython-{36m,37m}-x86_64-linux-gnu.so && \
    ${PYTHON_BIN} -m pip --no-cache-dir install --upgrade \
        pip \
        setuptools==41.0.0 && \
    python3 -m pip --no-cache-dir install --upgrade \
        pip \
        setuptools==41.0.0 && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/*

RUN alias python3="${PYTHON_BIN}" && \
    echo alias python3="${PYTHON_BIN}" >> ~/.bashrc && \
    echo alias python3="${PYTHON_BIN}" >> /home/openvino/.bashrc

#
# Change user to openvino
#
USER openvino
WORKDIR /home/openvino

ENTRYPOINT []
