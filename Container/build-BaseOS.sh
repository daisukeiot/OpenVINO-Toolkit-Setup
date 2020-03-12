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

#
# Build Ubuntu Base Image
#
docker build --squash --rm -f ./dockerfile/Dockerfile-Ubuntu --build-arg UBUNTU_VER=${UBUNTU_VER} -t ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER} .
docker push ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER}

echo ''
echo '###############################################################################'
docker run -it --rm ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER} /bin/bash -c "python3 --version;lsb_release -a"
