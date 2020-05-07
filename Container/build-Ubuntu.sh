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
./build-BaseOS.sh ${MY_REGISTRY} ${OS_VERSION} ${PYTHON_VERSION}

BASE_TAG=ubuntu_${OS_VERSION}_cp${PYTHON_VERSION}
./build-OpenVINO-Toolkit.sh ${MY_REGISTRY} ${BASE_TAG}

BASE_TAG=${BASE_TAG}_ov${OPENVINO_VER}
./build-Demo.sh ${MY_REGISTRY}/openvino-container:${BASE_TAG} 3.6
./build-Demo.sh ${MY_REGISTRY}/openvino-container:${BASE_TAG} 3.7

# For UP2
./build-Tensorflow.sh ${MY_REGISTRY} ${OS_VERSION} ${PYTHON_VERSION} ${TF_VERSION}

BASE_TAG=ubuntu_${OS_VERSION}_cp${PYTHON_VERSION}_tf${TF_VERSION}
./build-OpenVINO-Toolkit.sh ${MY_REGISTRY} ${BASE_TAG}

BASE_TAG=${BASE_TAG}_ov${OPENVINO_VER}
./build-Demo.sh ${MY_REGISTRY}/openvino-container:${BASE_TAG} 3.6
./build-Demo.sh ${MY_REGISTRY}/openvino-container:${BASE_TAG} 3.7

# docker rmi -f $(docker images -f "dangling=true" -q)