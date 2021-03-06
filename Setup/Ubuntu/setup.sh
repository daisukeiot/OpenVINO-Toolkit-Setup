#!/bin/bash

sudo apt-get update 
# install Python3.7 for AsyncIO
sudo apt-get install -y git curl python3-pip python3.7 python3.7-dev 
#
# install pip for python3.7
#
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py 
sudo -H python3.6 get-pip.py 
sudo -H python3.7 get-pip.py 
rm get-pip.py 
sudo -H python3.6 -m pip --no-cache-dir install --upgrade pip setuptools==41.0.0 
sudo -H python3.7 -m pip --no-cache-dir install --upgrade pip setuptools==41.0.0 

if [ ! -f "/usr/lib/python3/dist-packages/apt_pkg.cpython-37m-x86_64-linux-gnu.so" ]; then
    cd /usr/lib/python3/dist-packages
    sudo ln -s apt_pkg.cpython-{36m,37m}-x86_64-linux-gnu.so 
fi
#
# Install OpenVINO
#
OPENVINO_VER="2020.2.120" 
OPENVINO_PKG=l_openvino_toolkit_p_${OPENVINO_VER} 
OPENVINO_INSTALL=/opt/intel/openvino_${OPENVINO_VER} 
INTEL_OPENVINO_DIR=/opt/intel/openvino 
OPENVINO_DOWNLOAD=http://registrationcenter-download.intel.com/akdlm/irc_nas/16612/l_openvino_toolkit_p_2020.2.120.tgz 
#
# Temporary make Python3.7 to be default so OpenVINO scripts will install libraries for Python3.7
#
alias python3='python3.7' 
# echo alias python='python3.7'  >> ~/.bashrc 
#
# install numpy
#
sudo -H python3.7 -m pip install 'numpy==1.16' --force-reinstall 
#
# downlaod and install OpenVINO toolkit
#
mkdir /tmp/openvino 
cd /tmp/openvino 
# curl -LOJ "${OPENVINO_DOWNLOAD}" 
wget "${OPENVINO_DOWNLOAD}" 
tar -xzf ./*.tgz 
cd ${OPENVINO_PKG} 
./install.sh --list_components 
sed -i 's/decline/accept/g' silent.cfg 
sed -i 's/COMPONENTS=DEFAULTS/COMPONENTS=intel-openvino-ie-sdk-ubuntu-bionic__x86_64;intel-openvino-ie-rt-cpu-ubuntu-bionic__x86_64;intel-openvino-ie-rt-gpu-ubuntu-bionic__x86_64;intel-openvino-ie-rt-vpu-ubuntu-bionic__x86_64;intel-openvino-model-optimizer__x86_64;intel-openvino-opencv-lib-ubuntu-bionic__x86_64/g' silent.cfg 
sudo ./install.sh -s silent.cfg 
cd ~ 
rm -rf /tmp/openvino 
#
# install all dependencies
#
cd ${INTEL_OPENVINO_DIR}/install_dependencies 
sudo -H ./install_openvino_dependencies.sh 
source /opt/intel/openvino/bin/setupvars.sh -pyver 3.7 
echo "source ${INTEL_OPENVINO_DIR}/bin/setupvars.sh -pyver 3.7" >> ~/.bashrc 

#
# Configure Model Optimizer
#
cd ${INTEL_OPENVINO_DIR}/deployment_tools/model_optimizer/install_prerequisites 
sudo -H ./install_prerequisites.sh

#
# GPU
#
cd ${INTEL_OPENVINO_DIR}/install_dependencies 
sudo -H ./install_NEO_OCL_driver.sh 
sudo usermod -a -G video "$(whoami)" 

#
# VPU
#
cd ${INTEL_OPENVINO_DIR}/install_dependencies 
sudo usermod -a -G users "$(whoami)"
sudo -E ./install_NCS_udev_rules.sh

sudo reboot now
