if [ $# -eq 0 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version"
    echo "18.04 or 16.04"
    echo "======================================="
    exit
fi
#
# Build Container with verification script
# Built container but do not push to registry
#
UBUNTU_VER=$1
MY_REGISTRY=daisukeiot
OPENVINO_VER=2019.3.376
#
# Run Verification Script
#
docker run --rm -it -e "TARGET=CPU" ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify /home/openvino/verify.sh
docker run --rm -it -e "TARGET=GPU" --device /dev/dri ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify /home/openvino/verify.sh
docker run --rm -it -e "TARGET=MYRIAD" --privileged -v /dev:/dev --network=host ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify
