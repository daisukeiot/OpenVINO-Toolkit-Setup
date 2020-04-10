#
# Pass variables with --build-arg option
# OS_VERSION  : 16.04 or 18.04
# MY_REGISTRY : Your Container Registry
# 
ARG OS_VERSION=18.04
ARG MY_REGISTRY=daisukeiot
ARG TF_VERSION
ARG TAG_TF

FROM ${TAG_TF} as TensorFlow
WORKDIR /wheels/r1.14-py3.6.9
#
# Use Base image built in the previous step
#
FROM ${MY_REGISTRY}/openvino-container:baseos-ubuntu_${OS_VERSION}

#
# Local variables
#
ARG OPENVINO_VER=2019.3.376
ARG OPENVINO=l_openvino_toolkit_p_${OPENVINO_VER}
ARG OPENVINO_INSTALL=/opt/intel/openvino_${OPENVINO_VER}
ARG INSTALL_DIR=/opt/intel/openvino
ARG OPENVINO_DOWNLOAD=http://registrationcenter-download.intel.com/akdlm/irc_nas/16057/l_openvino_toolkit_p_2019.3.376.tgz

#
# Run as root to install OpenVINO Toolkit
#
USER root

#
# Use /tmp folder
#
WORKDIR /tmp
COPY --from=TensorFlow /wheels/*.whl .

#
# Download OpenVINO Toolkit
# Run silent install
# Setup environment variable
RUN pip3 install ./*.whl && \
    curl -LOJ "${OPENVINO_DOWNLOAD}" && \
    tar -xzf ./*.tgz && \
    cd l_openvino_toolkit* && \
    ./install.sh --list_components && \
    sed -i 's/decline/accept/g' silent.cfg && \
    ./install.sh -s silent.cfg && \
    # rm -rf /tmp/* && \
    cd $INSTALL_DIR/install_dependencies && \
    $INSTALL_DIR/install_dependencies/install_openvino_dependencies.sh && \
    echo "source $OPENVINO_INSTALL/bin/setupvars.sh" >> /home/openvino/.bashrc

ENV INSTALLDIR ${INSTALL_DIR}

#
# Set user to openvino and current directory to /home/openvino
#
USER openvino
WORKDIR /home/openvino

ENTRYPOINT []