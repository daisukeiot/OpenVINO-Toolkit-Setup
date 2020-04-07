if [ $# -ne 3 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version and reistry"
    echo "  Ubuntu Version : 18.04 or 16.04"
    echo "  Registry       : Your registry"
    echo "  Tensorflow     : Tensorflow Version"
    echo "  Example ./build-Ubuntu-UP2.sh 18.04 myregistry r1.14"
    echo "======================================="
    exit
fi

OS_VERSION=$1
MY_REGISTRY=$2
TF_VERSION=$3

TAG_OS=${MY_REGISTRY}/openvino-container:baseos-ubuntu_${OS_VERSION}

if docker inspect --type=image $TAG_OS > /dev/null 2>&1; then
    echo "${TAG_OS} exists"
  else
    ./Ubuntu/build-BaseOS.sh ${OS_VERSION} ${MY_REGISTRY}
fi

TAG_TF=${MY_REGISTRY}/openvino-container:tf_${TF_VERSION}

if docker inspect --type=image $TAG_TF > /dev/null 2>&1; then
    echo "${TAG_TF} exists"
  else
    ./Tensorflow/build-Tensorflow-NoAVX.sh ${OS_VERSION} ${MY_REGISTRY} ${TF_VERSION}
fi

./Ubuntu/build-OpenVINO-Toolkit-UP2.sh ${OS_VERSION} ${MY_REGISTRY} ${TF_VERSION}