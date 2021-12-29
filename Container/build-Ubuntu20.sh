
if [ $# -ne 1 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version and reistry"
    echo "  Registry       : Your registry"
    echo ""
    echo "  Example : ${0##*/} myregistry"
    echo "======================================="
    exit
fi
[ "$DEBUG" ] && set -x
SCRIPT_DIR=$(cd $(dirname $0); pwd)
clear

MY_REGISTRY=$1
OS_VERSION=20.04
OPENVINO_VER=2021.4.752
TAG=ubuntu_${OS_VERSION}

cd ./Ubuntu20
./build-BaseOS.sh ${MY_REGISTRY} ${OS_VERSION}

echo docker inspect --type=image ${MY_REGISTRY}/openvino-container:$TAG
if ! docker inspect --type=image ${MY_REGISTRY}/openvino-container:$TAG > /dev/null 2>&1; then
    echo "Failed to carete Ubuntu ${OS_VERSION} image"
    exit
fi


./build-OpenVINO-Toolkit.sh ${MY_REGISTRY} ${TAG}
TAG=${TAG}_ov${OPENVINO_VER}

if ! docker inspect --type=image ${MY_REGISTRY}/openvino-container:$TAG > /dev/null 2>&1; then
    echo "Failed to create OpenVINO image"
    exit
fi

# ./build-Demo.sh ${MY_REGISTRY}/openvino-container:${TAG}
# TAG=${TAG}_demo
# if ! docker inspect --type=image ${MY_REGISTRY}/openvino-container:$TAG > /dev/null 2>&1; then
#     echo "Failed to create image"
#     exit
# fi


# if [ $# -ne 2 ]
#   then
#     echo "======================================="
#     echo "Please specify Ubuntu Version and reistry"
#     echo "  Registry       : Your registry"
#     echo "  Ubuntu Version : 18.04 or 16.04"
#     echo "  Python         : Python Version"
#     echo ""
#     echo "  Example : ${0##*/} myregistry 18.04 3.7"
#     echo "======================================="
#     exit
# fi
# [ "$DEBUG" ] && set -x
# SCRIPT_DIR=$(cd $(dirname $0); pwd)
# clear

# MY_REGISTRY=$1
# OS_VERSION=$2

# cd ./Ubuntu20

# #
# # OpenVINO Toolkit ver 2021.4.752
# #
# OPENVINO_VER=2021.4.752
# TAG_BASE=ubuntu:${OS_VERSION}

# TAG=${MY_REGISTRY}/openvino-container:${OS_VERSION}_ov${OPENVINO_VER}

# if docker inspect --type=image $TAG > /dev/null 2>&1; then
#     echo "Deleting image"
#     docker rmi -f ${TAG}
# fi

# echo ''
# echo '    ____        _ __    __   _____ __             __ '
# echo '   / __ )__  __(_) /___/ /  / ___// /_____ ______/ /_'
# echo '  / __  / / / / / / __  /   \__ \/ __/ __ `/ ___/ __/'
# echo ' / /_/ / /_/ / / / /_/ /   ___/ / /_/ /_/ / /  / /_  '
# echo '/_____/\__,_/_/_/\__,_/   /____/\__/\__,_/_/   \__/  '
# echo ''
# echo '   ____                 _    _______   ______     ______            ____   _ __ '
# echo '  / __ \____  ___  ____| |  / /  _/ | / / __ \   /_  __/___  ____  / / /__(_) /_'
# echo ' / / / / __ \/ _ \/ __ \ | / // //  |/ / / / /    / / / __ \/ __ \/ / //_/ / __/'
# echo '/ /_/ / /_/ /  __/ / / / |/ // // /|  / /_/ /    / / / /_/ / /_/ / / ,< / / /_  '
# echo '\____/ .___/\___/_/ /_/|___/___/_/ |_/\____/    /_/  \____/\____/_/_/|_/_/\__/  '
# echo '    /_/                                                                         '
# echo ''
# echo "Image Tag  : ${TAG}"
# echo "Base Image : ${TAG_BASE}"
# echo "OpenVINO   : ${OPENVINO_VER}"
# echo ''
# #
# # Install OpenVINO Toolkit to Ubuntu Base Image
# #
# docker build --squash --rm -f ./Dockerfile -t ${TAG} \
#   --build-arg TAG_BASE=${TAG_BASE} \
#   --build-arg OPENVINO_VER=${OPENVINO_VER} \
#   ${SCRIPT_DIR}

# echo $'\n###############################################################################'
# echo '   ____                 _    _______   ______     ______            ____   _ __ '
# echo '  / __ \____  ___  ____| |  / /  _/ | / / __ \   /_  __/___  ____  / / /__(_) /_'
# echo ' / / / / __ \/ _ \/ __ \ | / // //  |/ / / / /    / / / __ \/ __ \/ / //_/ / __/'
# echo '/ /_/ / /_/ /  __/ / / / |/ // // /|  / /_/ /    / / / /_/ / /_/ / / ,< / / /_  '
# echo '\____/ .___/\___/_/ /_/|___/___/_/ |_/\____/    /_/  \____/\____/_/_/|_/_/\__/  '
# echo '    /_/                                                                         '
# echo ''
# echo "OpenVINO Toolkit : ${OPENVINO_VER}"
# echo "Image Tag        : ${TAG}"
# echo ''
# #
# # Check if the image exists or not
# #
# if ! docker inspect --type=image $TAG > /dev/null 2>&1; then
#     echo "Failed to create image"
#     exit
# fi

# echo $'\n###############################################################################'
# echo 'CTLC+C to cancel docker push'
# echo $'###############################################################################\n'
# read -t 10
# echo "Pushing Image : ${TAG}"
# echo ''
# # docker push ${TAG}

