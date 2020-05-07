if [ $# -ne 1 ]
  then
    echo "======================================="
    echo "Please specify base image tag and reistry"
    echo "  Image Tag      : Image Tag for a container with OpenVINO toolkit"
    echo "  Example ./build-app-container.sh myregistry/openvino-container:ubuntu18.04_openvino2020.2.120_cp3.7"
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