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

./Ubuntu/build-BaseOS.sh ${OS_VERSION} ${REPOSITORY}
./Ubuntu/build-OpenVINO-Toolkit.sh ${OS_VERSION} ${REPOSITORY}