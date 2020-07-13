#!/bin/bash

newHostName=RP-OpenVINO

OPENVINO_VER=2020.3.220
OPENVINO=l_openvino_toolkit_runtime_raspbian_p_${OPENVINO_VER}
INTEL_OPENVINO_DIR=/opt/intel/openvino
OPENVINO_DOWNLOAD=https://download.01.org/opencv/2020/openvinotoolkit/2020.3/${OPENVINO}.tgz

mkdir ~/OV.Work 
cd ~/OV.Work 

sudo apt-get update 
sudo apt-get install -y \
    build-essential \
    cmake \
    unzip \
    pkg-config \
    gfortran \
    curl \
    libgtk-3-dev \
    libatlas-base-dev \
    libcanberra-gtk* \
    libatlas-base-dev \
    gstreamer1.0-tools \
    libgstreamer1.0-0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    python3-pip

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py 
sudo -H python3.7 get-pip.py 

sudo mkdir -p /opt/intel/openvino 
wget ${OPENVINO_DOWNLOAD} 
sudo tar xf l_openvino_toolkit_runtime_raspbian_p*.tgz --strip 1 -C ${INTEL_OPENVINO_DIR}
#
# Replace OpenCV
#
curl https://packages.microsoft.com/config/debian/stretch/multiarch/prod.list > ./microsoft-prod.list
sudo cp ./microsoft-prod.list /etc/apt/sources.list.d/
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
sudo cp ./microsoft.gpg /etc/apt/trusted.gpg.d/
sudo apt-get update
sudo apt-get install -y moby-engine
sudo apt-get install -y moby-cli
sudo usermod -a -G docker "$(whoami)" 
rm ./microsoft*
sudo docker run --name opencv daisukeiot/openvino-container:raspbian_opencv_data /bin/bash 
sudo docker cp opencv:/data/opencv3.7.tar.gz ./
sudo tar -xf opencv3.7.tar.gz -C ${INTEL_OPENVINO_DIR} --strip-components 1

#
# Clean up docker
#
sudo docker system prune -a -f
sudo apt-get remove -y --purge moby-cli
sudo apt-get remove -y --purge moby-engine

echo "source $INTEL_OPENVINO_DIR/bin/setupvars.sh -pyver 3.7" >> ${HOME}/.bashrc 
source ${INTEL_OPENVINO_DIR}/bin/setupvars.sh -pyver 3.7
export PYTHONPATH=${INTEL_OPENVINO_DIR}/opencv3.7/lib/python2.7/dist-packages/:$PYTHONPATH
export PYTHONPATH=${INTEL_OPENVINO_DIR}/opencv3.7/lib/python3.7/dist-packages/:$PYTHONPATH
export LD_LIBRARY_PATH=${INTEL_OPENVINO_DIR}/opencv3.7/lib/:$LD_LIBRARY_PATH

sudo usermod -a -G users "$(whoami)" 
sh /opt/intel/openvino/install_dependencies/install_NCS_udev_rules.sh 
cd ~/
rm -r -f ~/OV.Work 
sudo raspi-config nonint do_expand_rootfs 
sudo raspi-config nonint do_memory_split 16 
sudo raspi-config nonint do_spi 0 
sudo raspi-config nonint do_boot_behaviour B2
sudo raspi-config nonint do_i2c 0 
sudo raspi-config nonint do_wifi_country US 
sudo raspi-config nonint do_change_locale en_US.UTF-8 
sudo raspi-config nonint do_configure_keyboard us
sudo raspi-config nonint do_change_timezone US/Pacific
sudo raspi-config nonint do_hostname $newHostName 
sudo reboot now