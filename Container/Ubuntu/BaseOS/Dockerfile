#
# Ubuntu Version
#
ARG OS_VERSION=18.04
FROM ubuntu:${OS_VERSION}

ARG OS_VERSION=18.04
RUN echo "Ubuntu Version ${OS_VERSION}"

ARG PYTHON_VERSION=3.7
ARG PYTHON=python${PYTHON_VERSION}
#
# Run as root user
#
USER root
WORKDIR /

#
# Install libraries
#
RUN apt-get update && \
    apt install -y --no-install-recommends \
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
                ${PYTHON} \
                ${PYTHON}-dev \
                python3-pip \
                udev \
                unzip \
                ocl-icd-libopencl1 \
                python3-setuptools \
                libpython3-dev \
                python3-wheel && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    ${PYTHON} get-pip.py && \
    rm /usr/bin/python3 && \
    alias python='${PYTHON}' && \
    echo alias python='${PYTHON}'  >> ~/.bashrc && \
    cd /usr/lib/python3/dist-packages && \
    sudo ln -s apt_pkg.cpython-{36m,37m}-x86_64-linux-gnu.so && \
    rm -rf /var/lib/apt/lists/*

RUN python3.7 -m pip --no-cache-dir install --upgrade \
    pip \
    setuptools==39.0.1

#
# Create user `openvino`
#
RUN useradd -ms /bin/bash -G video,users openvino && \
   chown openvino -R /home/openvino

#
# Change user to openvino
#
ENV USER=openvino
USER openvino
WORKDIR /home/openvino

RUN echo alias python='${PYTHON}'  >> ~/.bashrc

ENTRYPOINT []
