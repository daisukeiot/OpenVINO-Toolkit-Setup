#
# Pass variables with --build-arg option
# OS_VERSION  : 16.04 or 18.04
# MY_REGISTRY : Your Container Registry
# 
ARG OS_VERSION=18.04
ARG MY_REGISTRY=daisukeiot
ARG PYTHON_VERSION=3.7
ARG TF_VERSION=r1.15
ARG TAG_TF=

FROM ${TAG_TF} as TensorFlow

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
ARG PYTHON_VERSION=3.7
ARG PYTHON=python${PYTHON_VERSION}

#
# Run as root to install OpenVINO Toolkit
#
USER root

WORKDIR /tmp

#
# Copy Tensorflow Wheel Package
#
COPY --from=TensorFlow /wheels/*.whl .

RUN apt-get update && \
    apt install -y --no-install-recommends sudo python3-yaml python3-requests && \
    rm -rf /var/lib/apt/lists/* && \
    echo "openvino ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    usermod -aG video openvino 

#
# Install Tensorflow Package
#
RUN ${PYTHON} -m pip install ./*.whl

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
    echo "source ${INSTALL_DIR}/bin/setupvars.sh" >> /home/openvino/.bashrc && \
    /bin/bash -c "source ${INSTALL_DIR}/bin/setupvars.sh" && \
    cd ${INSTALL_DIR}/install_dependencies && \
    ./_install_all_dependencies.sh && \
    rm -rf /tmp/*

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
    ./install_NCS_udev_rules.sh"

ENTRYPOINT []