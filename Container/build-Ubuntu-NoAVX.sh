if [ $# -ne 3 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version and reistry"
    echo "  Registry       : Your registry"
    echo "  Ubuntu Version : 18.04 or 16.04"
    echo "  Python         : Python Version"
    echo ""
    echo "  Example : ${0##*/} myregistry 18.04 3.7"
    echo "======================================="
    exit
fi
[ "$DEBUG" ] && set -x
SCRIPT_DIR=$(cd $(dirname $0); pwd)
clear

MY_REGISTRY=$1
OS_VERSION=$2
PYTHON_VERSION=$3
TF_VERSION=1.15
OPENVINO_VER=2020.2.120

cd ./Ubuntu

TAG=ubuntu_${OS_VERSION}_cp${PYTHON_VERSION}

if ! docker inspect --type=image ${MY_REGISTRY}/openvino-container:$TAG > /dev/null 2>&1; then
    ./build-BaseOS.sh ${MY_REGISTRY} ${OS_VERSION} ${PYTHON_VERSION}
fi

if ! docker inspect --type=image ${MY_REGISTRY}/openvino-container:$TAG > /dev/null 2>&1; then
    echo "Failed to create image"
    exit
fi

./build-Tensorflow.sh ${MY_REGISTRY} ${TAG} ${TF_VERSION}
TAG=${TAG}_tf${TF_VERSION}
if ! docker inspect --type=image ${MY_REGISTRY}/openvino-container:$TAG > /dev/null 2>&1; then
    echo "Failed to create image"
    exit
fi

./build-OpenVINO-Toolkit.sh ${MY_REGISTRY} ${TAG}
TAG=${TAG}_ov${OPENVINO_VER}
if ! docker inspect --type=image ${MY_REGISTRY}/openvino-container:$TAG > /dev/null 2>&1; then
    echo "Failed to create image"
    exit
fi

./build-Demo.sh ${MY_REGISTRY}/openvino-container:${TAG}
TAG=${TAG}_demo
if ! docker inspect --type=image ${MY_REGISTRY}/openvino-container:$TAG > /dev/null 2>&1; then
    echo "Failed to create image"
    exit
fi

# docker rmi -f $(docker images -f "dangling=true" -q)