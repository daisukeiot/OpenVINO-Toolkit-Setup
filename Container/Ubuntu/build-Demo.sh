if [ $# -ne 2 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version and reistry"
    echo "  Base Tag       : Tag of image to run OpenVINO Demo"
    echo "  Python         : Python Version"
    echo "  Example ./build-Demo.sh myregistry daisukeiot/openvino-container:ubuntu18.04_ov2020.2.120_cp3.7 3.7"
    echo "======================================="
    exit
fi

[ "$DEBUG" ] && set -x
SCRIPT_DIR=$(cd $(dirname $0); pwd)

BASE_TAG=$1
PYTHON_VERSION=$2

TAG_BASE=${BASE_TAG}
TAG=${TAG_BASE}_demo_${PYTHON_VERSION}

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
echo "Image Tag  : ${TAG}"
echo "Base Image : ${TAG_BASE}"
echo ''
#
# Install OpenVINO Toolkit to Ubuntu Base Image
#
docker build --squash --rm -f ${SCRIPT_DIR}/OpenVINO-Demo/Dockerfile -t ${TAG} \
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
echo "Container built with Tensorflow version : ${TF_VER}"
echo "Image Tag : ${TAG}"
echo ''
echo $'\n###############################################################################'
echo 'CTLC+C to cancel docker push'
echo $'###############################################################################\n'
read -t 10
echo "Pushing Image : ${TAG}"
echo ''
docker push ${TAG}