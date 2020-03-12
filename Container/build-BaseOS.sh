UBUNTU_VER=$1
MY_REGISTRY=daisukeiot

#
# Build Ubuntu Base Image
#
docker build --squash --rm -f ./dockerfile/Dockerfile-Ubuntu --build-arg UBUNTU_VER=${UBUNTU_VER} -t ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER} .
# docker push ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER}

echo ''
echo '###############################################################################'
docker run -it --rm ${MY_REGISTRY}/openvino-toolkit:baseos-ubuntu_${UBUNTU_VER} /bin/bash -c "python3 --version;lsb_release -a"
