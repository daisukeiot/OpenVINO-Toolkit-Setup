if [ $# -ne 2 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version and reistry"
    echo "  Tag              : Tag for the image"
    echo "  Registry         : Your registry"
    echo "  Example ./build-OpenVINO-Toolkit.sh openvino myregistry"
    echo "======================================="
    exit
fi

IMAGE_TAG=$1
MY_REGISTRY=$2
TAG=${MY_REGISTRY}/openvino-container:openvino_${IMAGE_TAG}

docker image build -t ${TAG} OpenVINO-crosscompile