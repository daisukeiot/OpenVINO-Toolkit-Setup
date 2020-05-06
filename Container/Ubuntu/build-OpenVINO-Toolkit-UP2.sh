if [ $# -ne 4 ]
  then
    echo "======================================="
    echo "Please specify Ubuntu Version and reistry"
    echo "  Ubuntu Version : 18.04 or 16.04"
    echo "  Registry       : Your registry"
    echo "  Python         : Python Version"
    echo "  Tensorflow     : Tensorflow Version"
    echo "  Example ./build-OpenVINO-Toolkit.sh 18.04 myregistry 3.7 r1.15"
    echo "======================================="
    exit
fi

[ "$DEBUG" ] && set -x
SCRIPT_DIR=$(cd $(dirname $0); pwd)

#
# Use OpenVINO Toolkit ver 2020.2.120
#
OPENVINO_VER=2020.2.120
OS_VERSION=$1
MY_REGISTRY=$2
PYTHON_VERSION=$3
TF_VERSION=$4

TAG_TF=${MY_REGISTRY}/openvino-container:tf_${TF_VERSION}_cp${PYTHON_VERSION}
TAG=${MY_REGISTRY}/openvino-container:ubuntu${OS_VERSION}_openvino${OPENVINO_VER}_${TF_VERSION}_cp${PYTHON_VERSION}

if docker inspect --type=image $TAG > /dev/null 2>&1; then
    echo "Deleting image"
    docker rmi -f ${TAG}
fi

echo ''
echo '    ____        _ __    __   _____ __             __ '
echo '   / __ )__  __(_) /___/ /  / ___// /_____ ______/ /_'
echo '  / __  / / / / / / __  /   \__ \/ __/ __ `/ ___/ __/'
echo ' / /_/ / /_/ / / / /_/ /   ___/ / /_/ /_/ / /  / /_  '
echo '/_____/\__,_/_/_/\__,_/   /____/\__/\__,_/_/   \__/  '
echo ''
echo '   ____                 _    _______   ______     ______            ____   _ __     __  ______ ___ '
echo '  / __ \____  ___  ____| |  / /  _/ | / / __ \   /_  __/___  ____  / / /__(_) /_   / / / / __ \__ \'
echo ' / / / / __ \/ _ \/ __ \ | / // //  |/ / / / /    / / / __ \/ __ \/ / //_/ / __/  / / / / /_/ /_/ /'
echo '/ /_/ / /_/ /  __/ / / / |/ // // /|  / /_/ /    / / / /_/ / /_/ / / ,< / / /_   / /_/ / ____/ __/ '
echo '\____/ .___/\___/_/ /_/|___/___/_/ |_/\____/    /_/  \____/\____/_/_/|_/_/\__/   \____/_/   /____/ '
echo '    /_/                                                                                            '
echo ''
echo ''
echo "Image Tag      : ${TAG}"
echo "TensorFlow Tag : ${TAG_TF}"
echo ''
#
# Install OpenVINO Toolkit to Ubuntu Base Image
#
docker build --squash --rm \
  --build-arg OS_VERSION=${OS_VERSION} \
  --build-arg OPENVINO_VER=${OPENVINO_VER} \
  --build-arg MY_REGISTRY=${MY_REGISTRY} \
  --build-arg TF_VERSION=${TF_VERSION} \
  --build-arg TAG_TF=${TAG_TF} \
  -f ${SCRIPT_DIR}/OpenVINO-Toolkit-UP2/Dockerfile \
  -t ${TAG} \
  ${SCRIPT_DIR}

#
# Check if the image exists or not
#
if ! docker inspect --type=image $TAG > /dev/null 2>&1; then
    echo "Failed to create image"
    exit
fi

echo $'\n###############################################################################'
echo '   ____                 _    _______   ______     ______            ____   _ __     __  ______ ___ '
echo '  / __ \____  ___  ____| |  / /  _/ | / / __ \   /_  __/___  ____  / / /__(_) /_   / / / / __ \__ \'
echo ' / / / / __ \/ _ \/ __ \ | / // //  |/ / / / /    / / / __ \/ __ \/ / //_/ / __/  / / / / /_/ /_/ /'
echo '/ /_/ / /_/ /  __/ / / / |/ // // /|  / /_/ /    / / / /_/ / /_/ / / ,< / / /_   / /_/ / ____/ __/ '
echo '\____/ .___/\___/_/ /_/|___/___/_/ |_/\____/    /_/  \____/\____/_/_/|_/_/\__/   \____/_/   /____/ '
echo '    /_/                                                                                            '
echo ''
echo "Container built with OpenVINO Toolkit version : ${OPENVINO_VER}"
echo ''
echo $'\n###############################################################################'
echo 'CTLC+C to cancel docker push'
echo $'###############################################################################\n'

read -t 10
echo "Pushing Image : ${TAG}"
echo ''
docker push ${TAG}