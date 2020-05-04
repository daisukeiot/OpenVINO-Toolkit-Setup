#!/bin/bash

cd ~
sudo apt-get install -y curl && \
curl https://packages.microsoft.com/config/ubuntu/18.04/multiarch/prod.list > ./microsoft-prod.list && \
sudo cp ./microsoft-prod.list /etc/apt/sources.list.d/ && \
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg && \
sudo cp ./microsoft.gpg /etc/apt/trusted.gpg.d/ && \
rm microsoft* && \
sudo apt-get update && \
sudo apt-get install -y moby-engine && \
sudo apt-get install -y moby-cli && \
sudo usermod -aG docker $USER && \
TAG=daisukeiot/openvino-container:tf_r1.15_data && \
sudo docker run --name tensorflow ${TAG} /bin/true && \
sudo docker cp tensorflow:/tensorflow-1.15.2-cp37-cp37m-linux_x86_64.whl ./ && \
sudo docker rm tensorflow && \
sudo docker rmi -f ${TAG} && \
sudo apt-get install -y curl python3-pip python3.7 python3.7-dev && \
PATH=$PATH:$HOME/.local/bin && \
echo PATH=$PATH:$HOME/.local/bin >> ~/.bashrc && \
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
python3.7 get-pip.py && \
rm get-pip.py && \
cd /usr/lib/python3/dist-packages && \
sudo ln -s apt_pkg.cpython-{36m,37m}-x86_64-linux-gnu.so && \
cd ~ && \
python3.7 -m pip install 'numpy==1.16' --force-reinstall && \
python3.7 -m pip install ./*.whl && \
rm ./*.whl
