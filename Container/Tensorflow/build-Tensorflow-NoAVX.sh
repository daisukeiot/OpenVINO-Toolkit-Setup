if [ $# -ne 2 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version and reistry"
    echo "  Ubuntu Version : 18.04 or 16.04"
    echo "  Registry       : Your registry"
    echo "  Example ./build-Tensorflow.sh 18.04 myregistry"
    echo "======================================="
    exit
fi
SCRIPT_DIR=$(cd $(dirname $0); pwd)

OS_VERSION=$1
MY_REGISTRY=$2
TF_VERSION=r1.14
TAG=${MY_REGISTRY}/openvino-container:tf_${TF_VERSION}

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
# Build Ubuntu Base Image
#
docker build --squash --rm \
  -f ${SCRIPT_DIR}/NoAVX/Dockerfile \
  --build-arg OS_VERSION=${OS_VERSION} \
  --build-arg TF_VERSION=${TF_VERSION} \
  -t ${TAG} \
  ${SCRIPT_DIR}

echo '  ______                           ______             '
echo ' /_  __/__  ____  _________  _____/ __/ /___ _      __'
echo '  / / / _ \/ __ \/ ___/ __ \/ ___/ /_/ / __ \ | /| / /'
echo ' / / /  __/ / / (__  ) /_/ / /  / __/ / /_/ / |/ |/ / '
echo '/_/  \___/_/ /_/____/\____/_/  /_/ /_/\____/|__/|__/  '
echo '                                                      '
echo "Container built with Ubuntu ${OS_VERSION}"
echo ''
# echo "Pushing Image : ${TAG}"
# echo ''
# docker push ${TAG}

echo ''
echo '###############################################################################'
docker run -it --rm ${TAG} /bin/bash
