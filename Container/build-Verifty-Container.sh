if [ $# -ne 1 ]
  then
    echo "======================================="
    echo "Please specify Container"
    echo "  Example ./verify-container.sh myregistry/container:tag"
    echo "======================================="
    exit
fi

#
# Build Container with verification script
# Built container but do not push to registry
#
TAG=$1

docker build --squash --rm -f ./Common/Classification-Demo_Benchmark/Dockerfile -t ${TAG} --build-arg OPENVINO_IMAGE=${TAG} ./Common/Classification-Demo_Benchmark
