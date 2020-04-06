if [ $# -ne 2 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version and reistry"
    echo "  Ubuntu Version : 18.04 or 16.04"
    echo "  Registry       : Your registry"
    echo "  Example ./build-BaseOS.sh 18.04 myregistry"
    echo "======================================="
    exit
fi

UBUNTU_VER=$1
MY_REGISTRY=$2

TAG=${MY_REGISTRY}/openvino-container:baseos-ubuntu_${UBUNTU_VER}

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
docker build --squash --rm -f ./dockerfile/Dockerfile.BaseOS-Ubuntu --build-arg UBUNTU_VER=${UBUNTU_VER} -t ${TAG} .

echo '   __  ____                      __ '
echo '  / / / / /_  __  ______  __  __/ /_'
echo ' / / / / __ \/ / / / __ \/ / / / __/'
echo '/ /_/ / /_/ / /_/ / / / / /_/ / /_  '
echo '\____/_.___/\__,_/_/ /_/\__,_/\__/  '
echo '                                    '
echo ''
echo 
echo "Container built with OpenVINO Toolkit version : ${OPENVINO_VER}"
echo ''
# echo "Pushing Image : ${TAG}"
# echo ''
# docker push ${TAG}

echo ''
echo '###############################################################################'
docker run -it --rm $TAG} /bin/bash -c "python3 --version;lsb_release -a"
