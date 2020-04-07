#
# Ubuntu Version
#
ARG OS_VERSION=18.04
FROM ubuntu:${OS_VERSION}

ARG OS_VERSION=18.04
RUN echo "Ubuntu Version ${OS_VERSION}"
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
                python3-pip \
                udev \
                unzip \
                ocl-icd-libopencl1 \
                python3-setuptools \
                libpython3-dev \
                python3-wheel && \
    rm -rf /var/lib/apt/lists/*

#
# Create user `openvino`
#
RUN useradd -ms /bin/bash -G video,users openvino && \
   chown openvino -R /home/openvino

#
# Download and install OpenCL etc
#
RUN if [ "${OS_VERSION}" == "18.04" ] ; then \
    ( \
        cd /tmp/ && \
        curl -L "https://github.com/intel/compute-runtime/releases/download/20.09.15980/intel-gmmlib_19.4.1_amd64.deb" --output "intel-gmmlib_19.4.1_amd64.deb" && \
        curl -L "https://github.com/intel/compute-runtime/releases/download/20.09.15980/intel-igc-core_1.0.3445_amd64.deb" --output "intel-igc-core_1.0.3445_amd64.deb" && \
        curl -L "https://github.com/intel/compute-runtime/releases/download/20.09.15980/intel-igc-opencl_1.0.3445_amd64.deb" --output "intel-igc-opencl_1.0.3445_amd64.deb" && \
        curl -L "https://github.com/intel/compute-runtime/releases/download/20.09.15980/intel-opencl_20.09.15980_amd64.deb" --output "intel-opencl_20.09.15980_amd64.deb" && \
        curl -L "https://github.com/intel/compute-runtime/releases/download/20.09.15980/intel-ocloc_20.09.15980_amd64.deb" --output "intel-ocloc_20.09.15980_amd64.deb" && \
        dpkg -i ./*.deb && \
        ldconfig && \
        rm ./* \
    ); \
    fi
#
# Change user to openvino
#
ENV USER=openvino
USER openvino
WORKDIR /home/openvino

ENTRYPOINT []
