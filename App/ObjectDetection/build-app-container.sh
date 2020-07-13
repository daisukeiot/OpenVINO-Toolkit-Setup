if [ $# -ne 1 ]
  then
    echo "======================================="
    echo "Please specify base image tag and reistry"
    echo "  Image Tag      : Image Tag for a container with OpenVINO toolkit"
    echo "  Example : ${0##*/} myregistry/openvino-container:ubuntu18.04_openvino2020.3.194_cp3.7"
    echo "======================================="
    exit
fi
[ "$DEBUG" ] && set -x
SCRIPT_DIR=$(cd $(dirname $0); pwd)
clear

BASE_TAG=$1
TARGET_TAG=${BASE_TAG}_app

if [ -d "./Python/open_model_zoo" ]; then
  rm -r -f ./Python/open_model_zoo
fi

docker build --squash --rm \
    -f ./Dockerfile \
    --build-arg BASE_TAG=${BASE_TAG} \
    -t ${TARGET_TAG} \
    ${SCRIPT_DIR}

docker push ${TARGET_TAG}