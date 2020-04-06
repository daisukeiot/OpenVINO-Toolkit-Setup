if [ $# -ne 2 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version and reistry"
    echo "  Ubuntu Version : 18.04 or 16.04"
    echo "  Registry       : Your registry"
    echo "  Example ./build-OpenVINO-Toolkit.sh 18.04 myregistry"
    echo "======================================="
    exit
fi

[ "$DEBUG" ] && set -x
#
# Use OpenVINO Toolkit ver 2019.3.376
#
OPENVINO_VER=2019.3.376
OS_VERSION=$1
MY_REGISTRY=$2
TAG=${MY_REGISTRY}/openvino-container:ubuntu${OS_VERSION}_openvino${OPENVINO_VER}

echo ''
echo "Image Tag : ${TAG}"
echo ''

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
#
# Install OpenVINO Toolkit to Ubuntu Base Image
#
docker build --squash --rm -f ./OpenVINO-Toolkit/Dockerfile -t ${TAG} \
  --build-arg OS_VERSION=${OS_VERSION} \
  --build-arg OPENVINO_VER=${OPENVINO_VER} \
  --build-arg MY_REGISTRY=${MY_REGISTRY} .

#
# Check if the image exists or not
#
if ! docker inspect --type=image $TAG > /dev/null 2>&1; then
    echo "Failed to create image"
    exit
fi

echo '   ____                 _    _______   ______     ______            ____   _ __ '
echo '  / __ \____  ___  ____| |  / /  _/ | / / __ \   /_  __/___  ____  / / /__(_) /_'
echo ' / / / / __ \/ _ \/ __ \ | / // //  |/ / / / /    / / / __ \/ __ \/ / //_/ / __/'
echo '/ /_/ / /_/ /  __/ / / / |/ // // /|  / /_/ /    / / / /_/ / /_/ / / ,< / / /_  '
echo '\____/ .___/\___/_/ /_/|___/___/_/ |_/\____/    /_/  \____/\____/_/_/|_/_/\__/  '
echo '    /_/                                                                         '
echo ''
echo 
echo "Container built with OpenVINO Toolkit version : ${OPENVINO_VER}"
echo ''
# echo "Pushing Image : ${TAG}"
# echo ''
# docker push ${TAG}