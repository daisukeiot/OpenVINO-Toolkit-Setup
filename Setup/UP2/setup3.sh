#!/bin/bash

cd /tmp
sudo apt-get install -y curl

#
# Install Moby so we can copy Tensorflow withtou AVX from container image
#
curl https://packages.microsoft.com/config/ubuntu/18.04/multiarch/prod.list > ./microsoft-prod.list 
sudo cp ./microsoft-prod.list /etc/apt/sources.list.d/ 
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg 
sudo cp ./microsoft.gpg /etc/apt/trusted.gpg.d/ 
rm microsoft* 
sudo apt-get update 
sudo apt-get install -y moby-engine 
sudo apt-get install -y moby-cli 
sudo usermod -aG docker $USER 
TAG=daisukeiot/openvino-container:tf_r1.15_data 
sudo docker run --name tensorflow ${TAG} /bin/true 
sudo docker cp tensorflow:/tensorflow-1.15.2-cp37-cp37m-linux_x86_64.whl ./ 
#
# Clean up
#
sudo docker system prune -a -f
sudo apt-get remove -y --purge moby-cli
sudo apt-get remove -y --purge moby-engine

#
# Install Python 3.7 so we can install numpy v 1.16 before tensorflow
#
sudo apt-get install -y curl python3.7 python3.7-dev python3-pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py 
sudo -H python3.6 get-pip.py 
sudo -H python3.7 get-pip.py 
rm get-pip.py

if [ ! -f "/usr/lib/python3/dist-packages/apt_pkg.cpython-37m-x86_64-linux-gnu.so" ]; then
    cd /usr/lib/python3/dist-packages
    sudo ln -s apt_pkg.cpython-{36m,37m}-x86_64-linux-gnu.so 
fi
cd /tmp
sudo -H python3.7 -m pip install 'numpy==1.16' --force-reinstall
sudo -H python3.7 -m pip install ./*.whl
sudo rm ./*.whl
sudo apt autoremove -y
sudo reboot now
