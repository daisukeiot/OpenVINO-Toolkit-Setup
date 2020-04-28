if [ $# -ne 1 ]
  then
    echo "======================================="
    echo "Please specify Container"
    echo "  Example ./build-python-app-container.sh myregistry/container:tag"
    echo "======================================="
    exit
fi

#
# Build Container with verification script
# Built container but do not push to registry
#
SCRIPT_DIR=$(cd $(dirname $0); pwd)

BASE_TAG=$1
TARGET_TAG=$1_app_0.1
docker build --squash --rm \
    -f ./Dockerfile \
    --build-arg BASE_TAG=${BASE_TAG} \
    -t ${TARGET_TAG} \
    ${SCRIPT_DIR}
