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

OS_VERSION=$1
REPOSITORY=$2
PYTHON_VERSION=$3

cd ./Ubuntu
./build-BaseOS.sh ${OS_VERSION} ${REPOSITORY} ${PYTHON_VERSION}
./build-OpenVINO-Toolkit.sh ${OS_VERSION} ${REPOSITORY} ${PYTHON_VERSION}

docker rmi -f $(docker images -f "dangling=true" -q)