if [ $# -ne 3 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version and reistry"
    echo "  Registry       : Your registry"
    echo "  Ubuntu Version : 18.04 or 16.04"
    echo "  Python         : Python Version"
    echo ""
    echo "  Example : ${0##*/} myregistry 18.04 3.7"
    echo "======================================="
    exit
fi
[ "$DEBUG" ] && set -x
SCRIPT_DIR=$(cd $(dirname $0); pwd)
clear

MY_REGISTRY=$1
OS_VERSION=$2
PYTHON_VERSION=$3

TAG=${MY_REGISTRY}/openvino-container:ubuntu_${OS_VERSION}_cp${PYTHON_VERSION}

if docker inspect --type=image $TAG > /dev/null 2>&1; then
    echo "Deleting image"
    docker rmi -f ${TAG}
fi

echo $'\n###############################################################################\n'
echo '    ____        _ __    __   _____ __             __ '
echo '   / __ )__  __(_) /___/ /  / ___// /_____ ______/ /_'
echo '  / __  / / / / / / __  /   \__ \/ __/ __ `/ ___/ __/'
echo ' / /_/ / /_/ / / / /_/ /   ___/ / /_/ /_/ / /  / /_  '
echo '/_____/\__,_/_/_/\__,_/   /____/\__/\__,_/_/   \__/  '
echo ''

#
# Build Ubuntu Base Image
#
docker build --squash --rm \
  -f ${SCRIPT_DIR}/BaseOS/Dockerfile \
  --build-arg OS_VERSION=${OS_VERSION} \
  -t ${TAG} \
  ${SCRIPT_DIR}

echo $'\n###############################################################################'
echo '   __  ____                      __ '
echo '  / / / / /_  __  ______  __  __/ /_'
echo ' / / / / __ \/ / / / __ \/ / / / __/'
echo '/ /_/ / /_/ / /_/ / / / / /_/ / /_  '
echo '\____/_.___/\__,_/_/ /_/\__,_/\__/  '
echo ''
echo " Ubuntu version : ${OS_VERSION}"
echo " Python version : ${PYTHON_VERSION}"
echo " Image Tag      : ${TAG}"
echo $'\n###############################################################################\n'
#
# Check if the image exists or not
#
if ! docker inspect --type=image $TAG > /dev/null 2>&1; then
    echo "Failed to create image"
    exit
fi

docker run -it --rm ${TAG} /bin/bash -c "python${PYTHON_VERSION} --version;lsb_release -a"

echo $'\n###############################################################################'
echo 'CTLC+C to cancel docker push'
echo $'###############################################################################\n'
read -t 10
echo "Pushing Image : ${TAG}"
echo ''
docker push ${TAG}