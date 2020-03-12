MY_REGISTRY=daisukeiot

#
# Build Ubuntu 16.04 Base Image
#
UBUNTU_VER=16.04
docker build --squash --rm -f ./dockerfile/Dockerfile-Ubuntu${UBUNTU_VER} -t ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER} .
docker push ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER}

#
# Build Ubuntu 18.04 Base Image
#
UBUNTU_VER=18.04
docker build --squash --rm -f ./dockerfile/Dockerfile-Ubuntu${UBUNTU_VER} -t ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER} .
docker push ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER}

#
# Verification : Check OS Version and Python Version
#
UBUNTU_VER=16.04
echo ''
echo '###############################################################################'
docker run -it --rm ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER} /bin/bash -c "python3 --version;lsb_release -a"

UBUNTU_VER=18.04
echo ''
echo '###############################################################################'
docker run -it --rm ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER} /bin/bash -c "python3 --version;lsb_release -a"
