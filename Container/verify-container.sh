if [ $# -ne 2 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version and reistry"
    echo "  Ubuntu Version : 18.04 or 16.04"
    echo "  Registry       : Your registry"
    echo "  Example ./verify-container.sh 18.04 myregistry"
    echo "======================================="
    exit
fi

#
# Build Container with verification script
# Built container but do not push to registry
#
UBUNTU_VER=$1
MY_REGISTRY=$2
OPENVINO_VER=2019.3.376

#
# Image Classification Sample
#
docker run --rm -it -e "TARGET=CPU" ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify /home/openvino/verify.sh
docker run --rm -it -e "TARGET=GPU" --device /dev/dri ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify /home/openvino/verify.sh
docker run --rm -it -e "TARGET=MYRIAD" --privileged -v /dev:/dev --network=host ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify /home/openvino/verify.sh

#
# Benchmark Tool
#
docker run --rm -it -e "TARGET=CPU" ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify /home/openvino/benchmark.sh
docker run --rm -it -e "TARGET=GPU" --device /dev/dri ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify /home/openvino/benchmark.sh
docker run --rm -it -e "TARGET=MYRIAD" --privileged -v /dev:/dev --network=host ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify /home/openvino/benchmark.sh
