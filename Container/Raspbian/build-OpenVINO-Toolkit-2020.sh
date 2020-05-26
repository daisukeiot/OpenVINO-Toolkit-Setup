if [ $# -ne 2 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version and reistry"
    echo "  Raspbian Version : stretch, buster, etc"
    echo "  Registry         : Your registry"
    echo "  Example ./build-OpenVINO-Toolkit.sh buster myregistry"
    echo "======================================="
    exit
fi

# if [ ! -f ./qemu-arm-static ]; then
#     if [ ! -f /usr/bin/qemu-arm-static ]; then
#         sudo apt-get update
#         sudo apt-get install -y binfmt-support qemu qemu-user-static 
#     fi
#     cp /usr/bin/qemu-arm-static .
# fi

SCRIPT_DIR=$(cd $(dirname $0); pwd)

cp ${SCRIPT_DIR}/../../Setup/Raspbian/verification.sh ${SCRIPT_DIR}
#
# Use OpenVINO Toolkit ver 2020.1.023
#
OPENVINO_VER=2020.1.023
# https://hub.docker.com/r/balenalib/rpi-raspbian/tags

OS_VERSION=$1
MY_REGISTRY=$2
TAG=${MY_REGISTRY}/openvino-container:raspbian-${OS_VERSION}_${OPENVINO_VER}

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
  ${SCRIPT_DIR}/OpenVINO-Toolkit-2020/Dockerfile \
  -t ${TAG} \
  --build-arg OS_VERSION=${OS_VERSION} \
  --build-arg OPENVINO_VER=${OPENVINO_VER} \
  ${SCRIPT_DIR}

#
# Check if the image exists or not
#
if ! docker inspect --type=image $TAG > /dev/null 2>&1; then
    echo "Failed to create image"
    exit
fi

echo '   ____                 _    _______   ______ '
echo '  / __ \____  ___  ____| |  / /  _/ | / / __ \'
echo ' / / / / __ \/ _ \/ __ \ | / // //  |/ / / / /'
echo '/ /_/ / /_/ /  __/ / / / |/ // // /|  / /_/ / '
echo '\____/ .___/\___/_/ /_/|___/___/_/ |_/\____/  '
echo '    /_/                                       '
echo ''
echo '    ____                   __    _           '
echo '   / __ \____ __________  / /_  (_)___ _____ '
echo '  / /_/ / __ `/ ___/ __ \/ __ \/ / __ `/ __ \'
echo ' / _, _/ /_/ (__  ) /_/ / /_/ / / /_/ / / / /'
echo '/_/ |_|\__,_/____/ .___/_.___/_/\__,_/_/ /_/ '
echo '                /_/                          '
echo ''
echo 
echo "Container built with Raspbian version : ${OS_VERSION}"
echo "Container built with OpenVINO Toolkit : ${OPENVINO_VER}"
echo ''
echo "Pushing Image : ${TAG}"
echo ''
docker push ${TAG}
