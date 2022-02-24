#!/bin/bash

INTEL_OPENVINO_DIR=/opt/intel/openvino
OPENCL_VER=19.41.14441
OPENVINO_VER=2021.4.752
PYTHON_VER=python3.8

#
# Install libraries
#
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        autoconf \
        automake \
        build-essential \
        libtool \
        unzip \
        udev \
        gnupg

mkdir /tmp/openvino
cd /tmp/openvino
curl https://apt.repos.intel.com/openvino/2021/GPG-PUB-KEY-INTEL-OPENVINO-2021 > ./intel-key && \
sudo apt-key add ./intel-key

echo "deb https://apt.repos.intel.com/openvino/2021 all main" | sudo tee /etc/apt/sources.list.d/intel-openvino-2021.list

sudo apt update

sudo apt-get install -y intel-openvino-dev-ubuntu20-${OPENVINO_VER}
sudo ln --symbolic /opt/intel/openvino_${OPENVINO_VER}/ /opt/intel/openvino && \

sudo useradd -ms /bin/bash -G video,users $(whoami)
sudo rm -rf /tmp/openvino

cd ${INTEL_OPENVINO_DIR}/install_dependencies
sudo ./install_openvino_dependencies.sh -y -c=opencv_req -c=python -c=cl_compiler && \
sudo ./install_NEO_OCL_driver.sh --no_numa -y -d ${OPENCL_VER} && \
echo "source ${INTEL_OPENVINO_DIR}/bin/setupvars.sh" >> ~/.bashrc
${PYTHON_VER} -m pip install -r ${INTEL_OPENVINO_DIR}/python/requirements.txt
${PYTHON_VER} -m pip install -r ${INTEL_OPENVINO_DIR}/python/${PYTHON_VER}/requirements.txt