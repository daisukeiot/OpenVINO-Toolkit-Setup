if [ $# -ne 2 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version and reistry"
    echo "  Ubuntu Version : 18.04 or 16.04"
    echo "  Registry       : Your registry"
    echo "  Example ./build-verify-container.sh 18.04 myregistry"
    echo "======================================="
    exit
fi

#
# Build Container with verification script
# Built container but do not push to registry
#
UBUNTU_VER=$1
MY_REGISTRY=$2
OPENVINO_VER=2019.3.376

docker build --squash --rm -f ./dockerfile/Dockerfile.OpenVINO-Toolkit-Verification -t ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify --build-arg UBUNTU_VER=${UBUNTU_VER} --build-arg OPENVINO_VER=${OPENVINO_VER} --build-arg MY_REGISTRY=${MY_REGISTRY} .
