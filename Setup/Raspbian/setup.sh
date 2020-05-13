#!/bin/bash

newHostName=RP-OpenVINO

OPENVINO_VER=2020.1.023
OPENVINO=l_openvino_toolkit_runtime_raspbian_p_${OPENVINO_VER}
INSTALL_DIR=/opt/intel/openvino
OPENVINO_DOWNLOAD=https://download.01.org/opencv/2020/openvinotoolkit/2020.1/${OPENVINO}.tgz

sudo apt-get update 
sudo apt-get upgrade -y 
sudo apt-get install -y \
    build-essential \
    cmake \
    unzip \
    pkg-config \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libpng12-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libcanberra-gtk* \
    libatlas-base-dev \
    gfortran \
    python3-pip
mkdir ~/OV.Work 
cd ~/OV.Work 
sudo mkdir -p /opt/intel/openvino 
wget ${OPENVINO_DOWNLOAD} 
sudo tar xf l_openvino_toolkit_runtime_raspbian_p*.tgz --strip 1 -C ${INSTALL_DIR} 
echo "source $INSTALL_DIR/bin/setupvars.sh -pyver 3.7" >> ${HOME}/.bashrc 
source ${INSTALL_DIR}/bin/setupvars.sh 
sudo usermod -a -G users "$(whoami)" 
sh /opt/intel/openvino/install_dependencies/install_NCS_udev_rules.sh 
rm -r -f ~/OV.Work 
cd ~/
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