if [ $# -eq 0 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version"
    echo "18.04 or 16.04"
    echo "======================================="
    exit
fi
UBUNTU_VER=$1
MY_REGISTRY=daisukeiot

#
# Use OpenVINO Toolkit ver 2019.3.376
#
OPENVINO_VER=2019.3.376

#
# Install OpenVINO Toolkit to Ubuntu Base Image
#
docker build --squash --rm -f ./dockerfile/Dockerfile-OpenVINO-Toolkit -t ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER} --build-arg UBUNTU_VER=${UBUNTU_VER} --build-arg OPENVINO_VER=${OPENVINO_VER} .
docker push ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}
