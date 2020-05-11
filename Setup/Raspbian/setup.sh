#!/bin/bash

newHostName=rp4

OPENVINO_VER=2020.2.120
OPENVINO=l_openvino_toolkit_runtime_raspbian_p_${OPENVINO_VER}
INSTALL_DIR=/opt/intel/openvino
OPENVINO_DOWNLOAD=https://download.01.org/opencv/2020/openvinotoolkit/2020.2/${OPENVINO}.tgz

sudo apt-get update && \
sudo apt-get upgrade -y && \
sudo apt-get install -y cmake && \

mkdir ~/OV.Work && \
cd ~/OV.Work && \
sudo mkdir -p /opt/intel/openvino && \
wget ${OPENVINO_DOWNLOAD} && \
sudo tar xf l_openvino_toolkit_runtime_raspbian_p*.tgz --strip 1 -C ${INSTALL_DIR} && \
echo "source $INSTALL_DIR/bin/setupvars.sh" >> ${HOME}/.bashrc && \
source ${INSTALL_DIR}/bin/setupvars.sh && \
sh /opt/intel/openvino/install_dependencies/install_NCS_udev_rules.sh && \
sudo usermod -a -G users "$(whoami)" && \
sudo raspi-config nonint do_expand_rootfs && \
sudo raspi-config nonint do_memory_split 16 && \
sudo raspi-config nonint do_spi 0 && \
sudo raspi-config nonint do_i2c 0 && \
sudo raspi-config nonint do_wifi_country US && \
sudo raspi-config nonint do_change_locale en_US.UTF-8 && \
sudo raspi-config nonint do_configure_keyboard us && \
sudo raspi-config nonint do_hostname $newHostName && \
sudo reboot now