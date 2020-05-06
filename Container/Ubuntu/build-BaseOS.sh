if [ $# -ne 3 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version and reistry"
    echo "  Ubuntu Version : 18.04 or 16.04"
    echo "  Registry       : Your registry"
    echo "  Python         : Python Version"
    echo "  Example ./build-BaseOS.sh 18.04 myregistry 3.7"
    echo "======================================="
    exit
fi

clear

SCRIPT_DIR=$(cd $(dirname $0); pwd)
OS_VERSION=$1
MY_REGISTRY=$2
PYTHON_VERSION=$3

TAG=${MY_REGISTRY}/openvino-container:baseos-ubuntu_${OS_VERSION}_cp${PYTHON_VERSION}

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
echo "Container built with Ubuntu version : ${OS_VERSION}"
# echo "Pushing Image : ${TAG}"
# echo ''
# docker push ${TAG}

echo $'\n###############################################################################\n'
docker run -it --rm ${TAG} /bin/bash -c "python${PYTHON_VERSION} --version;lsb_release -a"

echo $'\n###############################################################################'
echo 'CTLC+C to cancel docker push'
echo $'###############################################################################\n'
echo ''
read -t 10
echo "Pushing Image : ${TAG}"
echo ''
docker push ${TAG}