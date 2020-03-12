#
# Build Container with verification script
# Built container but do not push to registry
#
MY_REGISTRY=daisukeiot
OPENVINO_VER=2019.3.376

#
# Ubuntu 16.04
#
UBUNTU_VER=16.04
docker build --squash --rm -f ./dockerfile/Dockerfile-OpenVINO-Toolkit-Verification -t ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify --build-arg UBUNTU_VER=${UBUNTU_VER} --build-arg OPENVINO_VER=${OPENVINO_VER} .
# docker push ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify
#
# Ubuntu 16.04
#
UBUNTU_VER=18.04
docker build --squash --rm -f ./dockerfile/Dockerfile-OpenVINO-Toolkit-Verification -t ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify --build-arg UBUNTU_VER=${UBUNTU_VER} --build-arg OPENVINO_VER=${OPENVINO_VER} .
# docker push ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify