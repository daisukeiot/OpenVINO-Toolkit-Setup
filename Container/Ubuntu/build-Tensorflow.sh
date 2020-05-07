if [ $# -ne 4 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version and reistry"
    echo "  Registry       : Your registry"
    echo "  Base Tag       : Tag of image to install Tensorflow"
    echo "  Python         : Python Version"
    echo "  Tensorflow     : Tensorflow Version"
    echo ""
    echo "  Example : ${0##*/} myregistry ubuntu_18.04_cp3.7 3.7 1.15"
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

TAG_BASE=${MY_REGISTRY}/openvino-container:${BASE_TAG}
TAG_TF=${MY_REGISTRY}/openvino-container:tf_r${TF_VERSION}_data
TAG=${MY_REGISTRY}/openvino-container:${BASE_TAG}_tf${TF_VERSION}

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
echo '  ______                           ______             '
echo ' /_  __/__  ____  _________  _____/ __/ /___ _      __'
echo '  / / / _ \/ __ \/ ___/ __ \/ ___/ /_/ / __ \ | /| / /'
echo ' / / /  __/ / / (__  ) /_/ / /  / __/ / /_/ / |/ |/ / '
echo '/_/  \___/_/ /_/____/\____/_/  /_/ /_/\____/|__/|__/  '
echo '                                                                            '
echo ''
echo "Image Tag  : ${TAG}"
echo "Base Image : ${TAG_BASE}"
echo "TF Image   : ${TAG_TF}"
#
# Install OpenVINO Toolkit to Ubuntu Base Image
#
docker build --squash --rm -f ${SCRIPT_DIR}/Tensorflow/Dockerfile -t ${TAG} \
  --build-arg TAG_TF=${TAG_TF} \
  --build-arg TAG_BASE=${TAG_BASE} \
  --build-arg PYTHON_VERSION=${PYTHON_VERSION} \
  ${SCRIPT_DIR}

#
# Check if the image exists or not
#
if ! docker inspect --type=image $TAG > /dev/null 2>&1; then
    echo "Failed to create image"
    exit
fi

echo $'\n###############################################################################'
echo '  ______                           ______             '
echo ' /_  __/__  ____  _________  _____/ __/ /___ _      __'
echo '  / / / _ \/ __ \/ ___/ __ \/ ___/ /_/ / __ \ | /| / /'
echo ' / / /  __/ / / (__  ) /_/ / /  / __/ / /_/ / |/ |/ / '
echo '/_/  \___/_/ /_/____/\____/_/  /_/ /_/\____/|__/|__/  '
echo ''
echo " Installed Tensorflow"
echo " Tensorflow version : ${TF_VER}"
echo " Image Tag          : ${TAG}"
echo ''
echo $'\n###############################################################################'
echo 'CTLC+C to cancel docker push'
echo $'###############################################################################\n'
read -t 10
echo "Pushing Image : ${TAG}"
echo ''
docker push ${TAG}