#!/bin/bash

OPENVINO_VER=2020.2.120
OPENVINO=l_openvino_toolkit_p_${OPENVINO_VER}
OPENVINO_INSTALL=/opt/intel/openvino_${OPENVINO_VER}
OPENVINO_DOWNLOAD=http://registrationcenter-download.intel.com/akdlm/irc_nas/16612/l_openvino_toolkit_p_2020.2.120.tgz
COMPONENTS='intel-OpenVINO-Toolkit-Setup__noarch;intel-openvino-model-optimizer__x86_64;intel-openvino-dldt-base__noarch;intel-openvino-setupvars__noarch;intel-openvino-eula__noarch;intel-openvino-ie-sdk-ubuntu-xenial__x86_64;intel-openvino-ie-bin-python-tools-ubuntu-xenial__x86_64;intel-openvino-ie-samples__x86_64;intel-openvino-ie-rt__x86_64;intel-openvino-ie-bin-3rd-debug__x86_64;intel-openvino-ie-rt-core-ubuntu-xenial__x86_64;intel-openvino-ie-rt-cpu-ubuntu-xenial__x86_64;intel-openvino-ie-rt-gpu-ubuntu-xenial__x86_64;intel-openvino-ie-rt-vpu-ubuntu-xenial__x86_64;intel-openvino-ie-rt-gna-ubuntu-xenial__x86_64;intel-openvino-ie-rt-hddl-ubuntu-xenial__x86_64;intel-openvino-omz-tools__x86_64;intel-openvino-docs__noarch;intel-openvino-gfx-driver-ubuntu-xenial__x86_64;intel-OpenVINO-Toolkit-Setup-pset'
sudo apt-get update
sudo apt-get install -y --no-install-recommends
wget -c ${OPENVINO_DOWNLOAD} -q && \
tar xf ${OPENVINO}.tgz && \
cd ${OPENVINO} && \
sed -i 's/decline/accept/g' silent.cfg && \
#sed -i "s/COMPONENTS=DEFAULTS/COMPONENTS=$COMPONENTS/g" silent.cfg && \    
sudo ./install.sh -s silent.cfg --ignore-signature
rm -rf ${OPENVINO} && \
rm -f ${OPENVINO}.tgz && \
/bin/bash -c "source $OPENVINO_INSTALL/bin/setupvars.sh" && \
cd $OPENVINO_INSTALL/deployment_tools/model_optimizer/install_prerequisites && \
./install_prerequisites.sh && \
cd $OPENVINO_INSTALL/install_dependencies/ && \
sudo usermod -a -G users "$(whoami)" && \
sudo sudo cp /opt/intel/openvino/inference_engine/external/97-myriad-usbboot.rules /etc/udev/rules.d/ && \
sudo udevadm control --reload-rules && \
sudo udevadm trigger && \
sudo ldconfig && \
sudo -E ./install_NEO_OCL_driver.sh && \
sudo apt autoremove -y && \
echo "source $OPENVINO_INSTALL/bin/setupvars.sh" >> /home/${USER}/.bashrc && \
sudo reboot now
