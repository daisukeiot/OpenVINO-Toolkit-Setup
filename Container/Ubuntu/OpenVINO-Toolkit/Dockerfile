#
# Pass variables with --build-arg option
# BASE_IMAGE  : Base Image to install OpenVINO 
# 
ARG TAG_BASE=ubuntu:18.04
FROM ${TAG_BASE}

#
# Variables that can be specified with --build-arg option
#
ARG OPENVINO_VER=2020.2.120
ARG OPENVINO=l_openvino_toolkit_p_${OPENVINO_VER}
ARG INTEL_OPENVINO_DIR=/opt/intel/openvino
ARG OPENVINO_DOWNLOAD=http://registrationcenter-download.intel.com/akdlm/irc_nas/16612/l_openvino_toolkit_p_2020.2.120.tgz
ARG PYTHON=python${PYTHON_VERSION}

#
# Run as root to install OpenVINO Toolkit
#
USER root
WORKDIR /tmp

RUN apt-get update && \
    apt install -y --no-install-recommends sudo && \
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
# install_NEO_OCL_driver.sh needs user name
# install USB rules
#
ENV USER openvino
RUN ./install_NEO_OCL_driver.sh && \
    ./install_NCS_udev_rules.sh && \
    echo "source ${INTEL_OPENVINO_DIR}/bin/setupvars.sh -pyver ${PYTHON_VERSION}" >> ~/.bashrc
#
# Install libusb
#
WORKDIR /tmp
RUN curl -L https://github.com/libusb/libusb/archive/v1.0.22.zip --output v1.0.22.zip && \
    unzip v1.0.22.zip && \
    cd libusb-1.0.22 && \
    ./bootstrap.sh && \
    ./configure --disable-udev --enable-shared && \
    make -j4

RUN apt-get update && \
    apt-get install -y --no-install-recommends libusb-1.0-0-dev && \
    rm -rf /var/lib/apt/lists/*

RUN cd /tmp/libusb-1.0.22/libusb && \
    /bin/mkdir -p '/usr/local/lib' && \
    /bin/bash ../libtool --mode=install /usr/bin/install -c libusb-1.0.la '/usr/local/lib' && \
    /bin/mkdir -p '/usr/local/include/libusb-1.0' && \
    /usr/bin/install -c -m 644 libusb.h '/usr/local/include/libusb-1.0' && \
    /bin/mkdir -p '/usr/local/lib/pkgconfig' && \
    cd /tmp/libusb-1.0.22/ && \
    /usr/bin/install -c -m 644 libusb-1.0.pc '/usr/local/lib/pkgconfig' && \
    ldconfig

#
# Clean up
#
RUN cd /tmp && rm -rf /tmp/*

#
# Switch user to openvino and current directory to /home/openvino
#
USER openvino
WORKDIR ${INTEL_OPENVINO_DIR}

ENTRYPOINT []