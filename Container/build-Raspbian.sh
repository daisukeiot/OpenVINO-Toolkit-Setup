if [ $# -ne 3 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version and reistry"
    echo "  Raspbian Version : stretch, buster, etc"
    echo "  Registry         : Your registry"
    echo "  Python           : Python Version"
    echo "  Example ./build-OpenVINO-Toolkit.sh buster myregistry 3.7"
    echo "======================================="
    exit
fi

OS_VERSION=$1
REPOSITORY=$2


./Raspbian/build-OpenVINO-Toolkit.sh ${OS_VERSION} ${REPOSITORY}
