if [ $# -eq 0 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version"
    echo "18.04 or 16.04"
    echo "======================================="
    exit
fi
#
# Build Container with verification script
# Built container but do not push to registry
#
UBUNTU_VER=$1
MY_REGISTRY=daisukeiot
OPENVINO_VER=2019.3.376

docker build --squash --rm -f ./dockerfile/Dockerfile-OpenVINO-Toolkit-Verification -t ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify --build-arg UBUNTU_VER=${UBUNTU_VER} --build-arg OPENVINO_VER=${OPENVINO_VER} .
