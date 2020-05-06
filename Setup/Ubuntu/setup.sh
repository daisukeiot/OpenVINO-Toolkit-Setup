#!/bin/bash

sudo apt-get update && \

# install Python3.7 for AsyncIO
sudo apt-get install -y git curl python3-pip python3.7 python3.7-dev && \
git clone https://github.com/daisukeiot/OpenVINO-Toolkit-Setup.git && \

# install pip for python3.7
PATH=$PATH:$HOME/.local/bin && \
echo PATH=$PATH:$HOME/.local/bin >> ~/.bashrc && \
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
python3.7 get-pip.py && \
rm get-pip.py && \
echo export $HOME/.local/bin >> $HOME/.bashrc

cd /usr/lib/python3/dist-packages && \
sudo ln -s apt_pkg.cpython-{36m,37m}-x86_64-linux-gnu.so

OPENVINO_VER=2020.2.120
OPENVINO_PKG=l_openvino_toolkit_p_${OPENVINO_VER}
OPENVINO_INSTALL=/opt/intel/openvino_${OPENVINO_VER}
OPENVINO_DIR=/opt/intel/openvino
OPENVINO_DOWNLOAD=http://registrationcenter-download.intel.com/akdlm/irc_nas/16612/l_openvino_toolkit_p_2020.2.120.tgz

# Temporary make Python3.7 to be default so OpenVINO scripts will install libraries for Python3.7
alias python='python3.7' && \
# echo alias python='python3.7'  >> ~/.bashrc && \

# install numpy
python3.7 -m pip install 'numpy==1.16' --force-reinstall && \

# downlaod and install OpenVINO toolkit
mkdir /tmp/openvino && \
cd /tmp/openvino && \
curl -LOJ "${OPENVINO_DOWNLOAD}" && \
tar -xzf ./*.tgz && \
cd ${OPENVINO_PKG} && \
./install.sh --list_components && \
sed -i 's/decline/accept/g' silent.cfg && \
sudo ./install.sh -s silent.cfg && \
cd ~ && \
rm -rf /tmp/openvino && \

# install all dependencies
cd ${OPENVINO_DIR}/install_dependencies && \
sudo -E ${OPENVINO_DIR}/install_dependencies/_install_all_dependencies.sh && \
sudo usermod -a -G video $USER && \
sudo usermod -a -G users $USER && \
sudo cp /opt/intel/openvino/inference_engine/external/97-myriad-usbboot.rules /etc/udev/rules.d/ && \
sudo udevadm control --reload-rules && \
sudo udevadm trigger && \
sudo ldconfig && \
echo "source ${OPENVINO_DIR}/bin/setupvars.sh" >> ~/.bashrc && \
source /opt/intel/openvino/bin/setupvars.sh && \

# install pre-req for model optimizer
cd ${OPENVINO_DIR}/deployment_tools/model_optimizer/install_prerequisites && \
sudo ./install_prerequisites.sh && \
sudo reboot now