if [ $# -ne 1 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version and reistry"
    echo "  Registry         : Your registry"
    echo "  Example ./build-OpenVINO-Toolkit.sh myregistry"
    echo "======================================="
    exit
fi

# https://github.com/opencv/opencv/wiki/Intel's-Deep-Learning-Inference-Engine-backend

SCRIPT_DIR=$(cd $(dirname $0); pwd)
MY_REGISTRY=$1

TAG=${MY_REGISTRY}/openvino-container:raspbian_opencv

if docker inspect --type=image $TAG > /dev/null 2>&1; then
    echo "Deleting image"
    docker rmi -f ${TAG}
fi

echo ''
echo '    ____        _ __    __   _____ __             __ '
echo '   / __ )__  __(_) /___/ /  / ___// /_____ ______/ /_'
echo '  / __  / / / / / / __  /   \__ \/ __/ __ `/ ___/ __/'
echo ' / /_/ / /_/ / / / /_/ /   ___/ / /_/ /_/ / /  / /_  '
echo '/_____/\__,_/_/_/\__,_/   /____/\__/\__,_/_/   \__/  '
echo ''
echo ''
echo "Image Tag : ${TAG}"
echo ''
#
# Build OpenCV for Raspbian
#
docker build --squash --rm -f \
  ${SCRIPT_DIR}/OpenCV-Python3.7/Dockerfile \
  -t ${TAG} \
  ${SCRIPT_DIR}

echo ''
echo ''
docker run  --name opencv ${TAG} /bin/true
docker cp opencv:/opencv.tar.gz .
docker rm opencv

TAG=${MY_REGISTRY}/openvino-container:raspbian_opencv_data

if docker inspect --type=image $TAG > /dev/null 2>&1; then
    echo "Deleting image"
    docker rmi -f ${TAG}
fi

docker build --squash --rm -f \
  ${SCRIPT_DIR}/OpenCV-Data/Dockerfile \
  -t ${TAG} \
  ${SCRIPT_DIR}

docker push ${TAG}