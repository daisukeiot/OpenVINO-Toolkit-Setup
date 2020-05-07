#
# Pass variables with --build-arg option
# OS_VERSION  : 16.04 or 18.04
# MY_REGISTRY : Your Container Registry
# 
ARG OS_VERSION=18.04
ARG MY_REGISTRY=daisukeiot
ARG PYTHON_VERSION=3.7
#
# Use Base image built in the previous step
#
FROM ${MY_REGISTRY}/openvino-container:baseos-ubuntu_${OS_VERSION}_cp${PYTHON_VERSION}

#
# Local variables
#
ARG OPENVINO_VER=2020.2.120
ARG OPENVINO=l_openvino_toolkit_p_${OPENVINO_VER}
ARG OPENVINO_INSTALL=/opt/intel/openvino_${OPENVINO_VER}
ARG INSTALL_DIR=/opt/intel/openvino
ARG OPENVINO_DOWNLOAD=http://registrationcenter-download.intel.com/akdlm/irc_nas/16612/l_openvino_toolkit_p_2020.2.120.tgz

#
# Run as root to install OpenVINO Toolkit
#
USER root
WORKDIR /tmp

RUN apt-get update && \
    apt install -y --no-install-recommends sudo python3-yaml python3-requests && \
    rm -rf /var/lib/apt/lists/* && \
    echo "openvino ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    usermod -aG video openvino && \
    usermod -aG users openvino

#
# Download OpenVINO Toolkit
# Run silent install
# Setup environment variable
#
RUN curl -LOJ "${OPENVINO_DOWNLOAD}" && \
    tar -xzf ./*.tgz && \
    cd l_openvino_toolkit* && \
    ./install.sh --list_components && \
    sed -i 's/decline/accept/g' silent.cfg && \
    ./install.sh -s silent.cfg && \
    ${INSTALL_DIR}/install_dependencies/_install_all_dependencies.sh

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

RUN cd /tmp && rm -rf /tmp/*

#
# Switch user to openvino and current directory to /home/openvino
#
USER openvino
WORKDIR /home/openvino

#
# Run as openvino user
#
RUN /bin/bash -c "source ${INSTALL_DIR}/bin/setupvars.sh && \
    cd ${INSTALL_DIR}/install_dependencies && \
    ./install_NCS_udev_rules.sh" && \
    echo "source ${INSTALL_DIR}/bin/setupvars.sh" >> /home/openvino/.bashrc

ENTRYPOINT []