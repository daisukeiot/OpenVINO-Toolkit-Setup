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

OS_VERSION=$1
REPOSITORY=$2
TF_VERSION=r1.14

if docker inspect --type=image $TAG_TF > /dev/null 2>&1; then
    echo "${TAG_TF} exists"
  else
    echo "Building Base OS Container" \
    # ./Ubuntu/build-BaseOS.sh ${OS_VERSION} ${REPOSITORY}
fi

TAG_TF=${MY_REGISTRY}/openvino-container:tf_${TF_VERSION}
echo ${TAG_TF}

if docker inspect --type=image $TAG_TF > /dev/null 2>&1; then
    echo "${TAG_TF} exists"
  else
    echo "Building Tensorflow" \
    #./Tensorflow/build-Tensorflow-NoAVX.sh ${OS_VERSION} ${REPOSITORY} ${TF_VERSION}
fi

./Ubuntu/build-OpenVINO-Toolkit-UP2.sh ${OS_VERSION} ${REPOSITORY} ${TF_VERSION}