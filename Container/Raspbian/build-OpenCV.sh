if [ $# -ne 1 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version and reistry"
    echo "  Registry         : Your registry"
    echo "  Example ./build-OpenVINO-Toolkit.sh myregistry"
    echo "======================================="
    exit
fi

TAG=${MY_REGISTRY}/openvino-container:raspbian-opencv

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
# Install OpenVINO Toolkit to Raspbian Base Image
#
docker build --squash --rm -f \
  ${SCRIPT_DIR}/OpenVINO-Toolkit/Dockerfile \
  -t ${TAG} \
  --build-arg OS_VERSION=${OS_VERSION} \
  --build-arg OPENVINO_VER=${OPENVINO_VER} \
  ${SCRIPT_DIR}