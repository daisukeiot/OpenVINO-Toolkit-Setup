if [ $# -ne 2 ]
  then
    echo "======================================="
    echo "Please specify base image tag and reistry"
    echo "  Image Tag      : Image Tag for a container with OpenVINO toolkit"
    echo "  Registry       : Your registry"
    echo "  Example ./build-app-container.sh openvino-container:ubuntu18.04_openvino2020.2.120_cp3.7 myregistry"
    echo "======================================="
    exit
fi
#
# Build Container with verification script
# Built container but do not push to registry
#
SCRIPT_DIR=$(cd $(dirname $0); pwd)

OPENVINO_VER=2020.2.120
MY_REGISTRY=$2
BASE_TAG=${MY_REGISTRY}/$1
TARGET_TAG=${BASE_TAG}_app

docker build --squash --rm \
    -f ./Dockerfile \
    --build-arg BASE_TAG=${BASE_TAG} \
    -t ${TARGET_TAG} \
    ${SCRIPT_DIR}

dicker push ${TARGET_TAG}