MY_REGISTRY=daisukeiot

#
# Use OpenVINO Toolkit ver 2019.3.376
#
OPENVINO_VER=2019.3.376

#
# Install OpenVINO Toolkit to Ubuntu 16.04 Base Image
#
UBUNTU_VER=16.04
docker build --squash --rm -f ./dockerfile/Dockerfile-OpenVINO-Toolkit -t ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER} --build-arg UBUNTU_VER=${UBUNTU_VER} --build-arg OPENVINO_VER=${OPENVINO_VER} .
docker push ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}

#
# Install OpenVINO Toolkit to Ubuntu 18.04 Base Image
#
UBUNTU_VER=18.04
docker build --squash --rm -f ./dockerfile/Dockerfile-OpenVINO-Toolkit -t ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER} --build-arg UBUNTU_VER=${UBUNTU_VER} --build-arg OPENVINO_VER=${OPENVINO_VER} .
docker push ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}
