# Object Detection app

## Setup

- Ubuntu 18.04
- Python 3.7
- OpenVINO 2020.2.120

## Ubuntu

Install Python3.7 and make it default

```bash
sudo apt-get update && \
sudo apt-get install -y openssh-server git curl && \
sudo apt-get install -y python3-pip && \
sudo apt-get install -y python3.7 python3.7-dev && \
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
python3.7 get-pip.py && \
rm get-pip.py && \
sudo rm /usr/bin/python3 && \
sudo ln -s python3.7 /usr/bin/python3 && \
alias python='python3.7' && \
echo alias python='python3.7'  >> ~/.bashrc && \
sudo apt-get remove --purge python3-apt && \
sudo apt-get install --reinstall python3-apt && \
pip3 install 'numpy==1.16' --force-reinstall \
```

## OpenVINO

Install 2020.2.120

```bash
export OPENVINO_VER=2020.2.120
export OPENVINO=l_openvino_toolkit_p_${OPENVINO_VER}
export OPENVINO_INSTALL=/opt/intel/openvino_${OPENVINO_VER}
export INSTALL_DIR=/opt/intel/openvino
export OPENVINO_DOWNLOAD=http://registrationcenter-download.intel.com/akdlm/irc_nas/16612/l_openvino_toolkit_p_2020.2.120.tgz
mkdir /tmp/openvino
cd /tmp/openvino && \
curl -LOJ "${OPENVINO_DOWNLOAD}" && \
tar -xzf ./*.tgz && \
cd $OPENVINO && \
./install.sh --list_components && \
sed -i 's/decline/accept/g' silent.cfg && \
sudo ./install.sh -s silent.cfg && \
cd ~ && \
rm -rf /tmp/openvino && \
cd $INSTALL_DIR/install_dependencies && \
sudo -E $INSTALL_DIR/install_dependencies/install_openvino_dependencies.sh && \
sudo usermod -a -G users $USER && \
sudo cp /opt/intel/openvino/inference_engine/external/97-myriad-usbboot.rules /etc/udev/rules.d/ && \
sudo udevadm control --reload-rules && \
sudo udevadm trigger && \
sudo ldconfig && \
echo "source $OPENVINO_INSTALL/bin/setupvars.sh" >> ~/.bashrc && \
source /opt/intel/openvino/bin/setupvars.sh && \
cd $OPENVINO_INSTALL/deployment_tools/model_optimizer/install_prerequisites && \
sudo ./install_prerequisites.sh
```

Install Video Driver

```bash
sudo usermod -a -G video $USER
sudo -E su
cd $INSTALL_DIR/install_dependencies && \
./install_NEO_OCL_driver.sh
```
