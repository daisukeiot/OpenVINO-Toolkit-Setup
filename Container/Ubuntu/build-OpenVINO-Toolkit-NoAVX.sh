if [ $# -ne 4 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version and reistry"
    echo "  Registry       : Your registry"
    echo "  Base Tag       : Tag of image to install Tensorflow"
    echo "  Python         : Python Version"
    echo "  Tensorflow     : Tensorflow Version"
    echo ""
    echo "  Example : ${0##*/} myregistry 18.04 3.7 1.15"
    echo "======================================="
    exit
fi
[ "$DEBUG" ] && set -x
SCRIPT_DIR=$(cd $(dirname $0); pwd)
clear

MY_REGISTRY=$1
BASE_TAG=$2
PYTHON_VERSION=$3
TF_VERSION=$4

#
# OpenVINO Toolkit ver 2020.2.120
#
OPENVINO_VER=2020.2.120

BASE_TAG=${MY_REGISTRY}/openvino-container:${BASE_TAG}
TAG=${MY_REGISTRY}/openvino-container:${BASE_TAG}_ov${OPENVINO_VER}

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
echo '   ____                 _    _______   ______     ______            ____   _ __ '
echo '  / __ \____  ___  ____| |  / /  _/ | / / __ \   /_  __/___  ____  / / /__(_) /_'
echo ' / / / / __ \/ _ \/ __ \ | / // //  |/ / / / /    / / / __ \/ __ \/ / //_/ / __/'
echo '/ /_/ / /_/ /  __/ / / / |/ // // /|  / /_/ /    / / / /_/ / /_/ / / ,< / / /_  '
echo '\____/ .___/\___/_/ /_/|___/___/_/ |_/\____/    /_/  \____/\____/_/_/|_/_/\__/  '
echo '    /_/                                                                         '
echo ''
echo "Image Tag  : ${TAG}"
echo "Base Image : ${BASE_TAG}"
echo "OpenVINO   : ${OPENVINO_VER}"
echo ''
#
# Install OpenVINO Toolkit to Ubuntu Base Image
#
docker build --squash --rm -f ${SCRIPT_DIR}/OpenVINO-Toolkit/Dockerfile -t ${TAG} \
  --build-arg BASE_IMAGE=${BASE_TAG} \
  --build-arg OPENVINO_VER=${OPENVINO_VER} \
  ${SCRIPT_DIR}

#
# Check if the image exists or not
#
if ! docker inspect --type=image $TAG > /dev/null 2>&1; then
    echo "Failed to create image"
    exit
fi

echo $'\n###############################################################################'
echo '   ____                 _    _______   ______     ______            ____   _ __ '
echo '  / __ \____  ___  ____| |  / /  _/ | / / __ \   /_  __/___  ____  / / /__(_) /_'
echo ' / / / / __ \/ _ \/ __ \ | / // //  |/ / / / /    / / / __ \/ __ \/ / //_/ / __/'
echo '/ /_/ / /_/ /  __/ / / / |/ // // /|  / /_/ /    / / / /_/ / /_/ / / ,< / / /_  '
echo '\____/ .___/\___/_/ /_/|___/___/_/ |_/\____/    /_/  \____/\____/_/_/|_/_/\__/  '
echo '    /_/                                                                         '
echo ''
echo "OpenVINO Toolkit : ${OPENVINO_VER}"
echo "Image Tag        : ${TAG}"
echo ''
echo $'\n###############################################################################'
echo 'CTLC+C to cancel docker push'
echo $'###############################################################################\n'
read -t 10
echo "Pushing Image : ${TAG}"
echo ''
docker push ${TAG}