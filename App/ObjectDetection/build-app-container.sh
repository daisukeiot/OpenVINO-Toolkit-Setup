if [ $# -ne 2 ]
  then
    echo "======================================="
    echo "Please specify base image tag and reistry"
    echo "  Image Tag      : Image Tag for a container with OpenVINO toolkit"
    echo "  Python         : Python Version"
    echo "  Example : ${0##*/} myregistry/openvino-container:ubuntu18.04_openvino2020.2.120_cp3.7 3.7"
    echo "======================================="
    exit
fi
[ "$DEBUG" ] && set -x
SCRIPT_DIR=$(cd $(dirname $0); pwd)
clear

BASE_TAG=$1
PYTHON_VERSION=$2
TARGET_TAG=${BASE_TAG}_app

if [ -d "./Python/open_model_zoo" ]; then
  rm -r -f ./Python/open_model_zoo
fi

docker build --squash --rm \
    -f ./Dockerfile \
    --build-arg BASE_TAG=${BASE_TAG} \
    --build-arg PYTHON_VERSION=${PYTHON_VERSION} \
    -t ${TARGET_TAG} \
    ${SCRIPT_DIR}

docker push ${TARGET_TAG}