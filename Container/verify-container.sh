#
# Build Container with verification script
# Built container but do not push to registry
#
MY_REGISTRY=daisukeiot
OPENVINO_VER=2019.3.376
#
# Run Verification Script
#
UBUNTU_VER=16.04
docker run --rm -it -e "TARGET=CPU" ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify
docker run --rm -it -e "TARGET=GPU" --device /dev/dri ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify
docker run --rm -it -e "TARGET=MYRIAD" --privileged -v /dev:/dev ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify

UBUNTU_VER=18.04
docker run --rm -it -e "TARGET=CPU" ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify
docker run --rm -it -e "TARGET=GPU" --device /dev/dri ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify
docker run --rm -it -e "TARGET=MYRIAD" --privileged -v /dev:/dev ${MY_REGISTRY}/openvino-toolkit:${UBUNTU_VER}_${OPENVINO_VER}_verify
