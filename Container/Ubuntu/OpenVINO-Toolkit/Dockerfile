#
# Pass variables with --build-arg option
# BASE_IMAGE  : Base Image to install OpenVINO 
# 
ARG TAG_BASE=ubuntu:18.04
FROM ${TAG_BASE}

#
# Variables that can be specified with --build-arg option
#
ARG OPENVINO_VER=2020.3.194
ARG OPENVINO=l_openvino_toolkit_p_${OPENVINO_VER}
ARG INTEL_OPENVINO_DIR=/opt/intel/openvino
ARG OPENVINO_DOWNLOAD=http://registrationcenter-download.intel.com/akdlm/irc_nas/16612/l_openvino_toolkit_p_2020.3.194.tgz

#
# Run as root to install OpenVINO Toolkit
#
USER root
WORKDIR /tmp

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        sudo \
        python3-yaml \
        python3-requests && \
    rm -rf /var/lib/apt/lists/* && \
    echo "openvino ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    usermod -aG video openvino && \
    usermod -aG users openvino

#
# Download OpenVINO Toolkit and run silent install
#
RUN curl -LOJ "${OPENVINO_DOWNLOAD}" && \
    tar -xzf ./*.tgz && \
    cd l_openvino_toolkit* && \
    ./install.sh --list_components && \
    sed -i 's/decline/accept/g' silent.cfg && \
    ./install.sh -s silent.cfg

WORKDIR ${INTEL_OPENVINO_DIR}/install_dependencies

#
# Switch shell
#
SHELL ["/bin/bash", "-c"] 

#
# install_NEO_OCL_driver.sh needs user name
# install USB rules
#
ENV USER openvino
RUN source ${INTEL_OPENVINO_DIR}/bin/setupvars.sh -pyver ${PYTHON_VERSION} && \
    ./install_NEO_OCL_driver.sh && \
    ./install_NCS_udev_rules.sh && \
    echo "source ${INTEL_OPENVINO_DIR}/bin/setupvars.sh -pyver ${PYTHON_VERSION}" >> /home/openvino/.bashrc && \
    echo "source ${INTEL_OPENVINO_DIR}/bin/setupvars.sh -pyver ${PYTHON_VERSION}" >> ~/.bashrc
#
# Install libusb
#
WORKDIR /tmp
RUN wget https://github.com/libusb/libusb/archive/v1.0.23.tar.gz && \
    tar xzvf v1.0.23.tar.gz && \
    cd libusb-1.0.23 && \
    ./bootstrap.sh && \
    ./configure --disable-udev --enable-shared  && \
    make && \
    make install && \
    ldconfig /usr/local/lib

#
# Clean up
#
RUN rm -rf /tmp/*

#
# Switch shell
#
SHELL ["/bin/sh", "-c"] 

#
# Switch user to openvino and current directory to /home/openvino
#
USER openvino
WORKDIR ${INTEL_OPENVINO_DIR}

ENTRYPOINT []