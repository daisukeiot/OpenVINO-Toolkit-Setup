#
# Pass variables with --build-arg option
# OS_VERSION  : 16.04 or 18.04
# MY_REGISTRY : Your Container Registry
# 
ARG OS_VERSION=18.04
ARG MY_REGISTRY=daisukeiot
ARG TF_VERSION=r1.15
ARG TAG_TF=
ARG PYTHON_VERSION=3.7

FROM ${TAG_TF} as TensorFlow
WORKDIR /wheels
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

ENV PYTHON=python${PYTHON_VERSION}

#
# Run as root to install OpenVINO Toolkit
#
USER root

#
# Use /tmp folder
#
WORKDIR /tmp

COPY --from=TensorFlow /wheels/*.whl .

RUN apt-get update && \
    apt install -y --no-install-recommends sudo && \
    rm -rf /var/lib/apt/lists/* && \
    echo "openvino ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
#
# Download OpenVINO Toolkit
# Run silent install
# Setup environment variable
RUN ${PYTHON} -m pip install ./*.whl && \
    curl -LOJ "${OPENVINO_DOWNLOAD}" && \
    tar -xzf ./*.tgz && \
    cd l_openvino_toolkit* && \
    ./install.sh --list_components && \
    sed -i 's/decline/accept/g' silent.cfg && \
    ./install.sh -s silent.cfg && \
    rm -rf /tmp/* && \
    echo "source $OPENVINO_INSTALL/bin/setupvars.sh" >> /home/openvino/.bashrc

RUN cd $INSTALL_DIR/install_dependencies && \
    sudo -E ./install_openvino_dependencies.sh && \
    sudo -E ./install_NEO_OCL_driver.sh

ENV INSTALLDIR ${INSTALL_DIR}

#
# Set user to openvino and current directory to /home/openvino
#
USER openvino
WORKDIR /home/openvino

#
# Run as openvino user
#
RUN /bin/bash -c "source $INSTALL_DIR/bin/setupvars.sh && \
    cd $INSTALL_DIR/install_dependencies && \
    ./install_NCS_udev_rules.sh"

ENTRYPOINT []