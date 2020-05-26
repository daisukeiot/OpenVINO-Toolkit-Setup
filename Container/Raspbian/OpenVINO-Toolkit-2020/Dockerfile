#
# Pass variables with --build-arg option
# OS_VERSION  : buster or stretch
# MY_REGISTRY : Your Container Registry
# 
# Reference
# https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_raspbian.html
# https://www.intel.com/content/www/us/en/support/articles/000055220/boards-and-kits.html 
# CMake > 3.7.2
# Python 3.5
#
ARG OS_VERSION=buster
 
#
# Use Base image built in the previous step
#
FROM balenalib/rpi-raspbian:${OS_VERSION}

FROM ie_cross_armhf:lates as openvino_bin

ARG OPENVINO_VER=2020.1.023
ARG OPENVINO=l_openvino_toolkit_runtime_raspbian_p_${OPENVINO_VER}
ENV INTEL_OPENVINO_DIR=/opt/intel/openvino
ARG OPENVINO_DOWNLOAD=https://download.01.org/opencv/2020/openvinotoolkit/2020.1/${OPENVINO}.tgz
 
#
# Run as root to install OpenVINO Toolkit Runtime
#
USER root
 
 
#
# balenalib image already has QEMU installed.  Enable for non-Balena base image
#
# RUN [ "cross-build-start" ]
# ADD ./qemu-arm-static /usr/bin/
 
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        apt-utils \
        automake \
        cmake \
        cpio \
        gcc \
        g++ \
        libatlas-base-dev \
        libgtk-3-dev \
        libstdc++6 \
        libtool \
        lsb-release \
        make \
        nano \
        python3-pip \
        python3-numpy \
        python3-scipy \
        python3.7-dev \
        autoconf \
        unzip \
        wget && \
    apt-get autoremove && \
    rm -rf /var/lib/apt/lists/*
 
#
# Create user `openvino`
#
RUN useradd -ms /bin/bash openvino && \
    chown openvino -R /home/openvino && \
    echo "openvino ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
 
#
# Use /tmp folder
#
WORKDIR /tmp
 
#
# Install openvino package
# Run setupvars.sh for python 3.7
#
RUN wget -c ${OPENVINO_DOWNLOAD} && \
    mkdir -p ${INTEL_OPENVINO_DIR} && \
    tar xzvf l_openvino_toolkit_runtime_raspbian_p*.tgz --strip 1 -C ${INTEL_OPENVINO_DIR} && \
    echo "source /opt/intel/openvino/bin/setupvars.sh -pyver 3.7" >> ~/.bashrc && \
    echo "source $INTEL_OPENVINO_DIR/bin/setupvars.sh -pyver 3.7">> /home/openvino/.bashrc
 
#
# Add USB Rule.  With this, you must run with --privilege and --network=host
# Enable if you prefer –privilege mode
#
# RUN /bin/bash -c "source $INTEL_OPENVINO_DIR/bin/setupvars.sh && \
#     sh $INTEL_OPENVINO_DIR/install_dependencies/install_NCS_udev_rules.sh"
 
#
# Install libusb to find Movidius device to run in non-privileged
#
RUN wget https://github.com/libusb/libusb/archive/v1.0.23.tar.gz && \
    tar xzvf v1.0.23.tar.gz && \
    cd libusb-1.0.23 && \
    ./bootstrap.sh && \
    ./configure --disable-udev --enable-shared  && \
    make && \
    make install && \
    ldconfig /usr/local/lib
 
#
# Switch to home folder
#
WORKDIR /home/openvino


COPY --from=openvino_bin /openvino/bin/armv7l/Release .

#
# Add script for verification
#
ADD ./verification.sh .
 
#
# Clean Up
#
RUN rm -f -r /tmp/* && \
    chmod 777 ./verification.sh
 
# RUN [ "cross-build-end" ]
 
#
# Switch shell
#
SHELL ["/bin/bash", "-c"] 
 
USER openvino
 
# ENTRYPOINT ["/bin/bash", "-c", "source ${INTEL_OPENVINO_DIR}/bin/setupvars.sh"]
CMD []
