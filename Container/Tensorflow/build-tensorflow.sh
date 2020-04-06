#!/usr/bin/env bash

set -e

export TF_VERSION_GIT_TAG=r1.14

GCC_VERSION="7"
update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-$GCC_VERSION 10
update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-$GCC_VERSION 10
update-alternatives --set gcc "/usr/bin/gcc-$GCC_VERSION"
update-alternatives --set g++ "/usr/bin/g++-$GCC_VERSION"
gcc --version

pip install -U --user pip six numpy wheel setuptools mock 'future>=0.17.1'
pip install -U --user keras_applications --no-deps
pip install -U --user keras_preprocessing --no-deps

cd /
rm -fr tensorflow/
git clone --depth 1 --branch $TF_VERSION_GIT_TAG "https://github.com/tensorflow/tensorflow.git"

TF_ROOT=/tensorflow
cd $TF_ROOT

export USE_GPU=0

# Python path options
export PYTHON_BIN_PATH=$(which python3)
export PYTHON_LIB_PATH="$($PYTHON_BIN_PATH -c 'import site; print(site.getsitepackages()[0])')"
export PYTHONPATH=${TF_ROOT}/lib
export PYTHON_ARG=${TF_ROOT}/lib

# Compilation parameters
export TF_NEED_CUDA=0
export TF_NEED_GCP=0
export TF_CUDA_COMPUTE_CAPABILITIES=5.2,3.5
export TF_NEED_HDFS=0
export TF_NEED_OPENCL=1
export TF_NEED_JEMALLOC=1  # Need to be disabled on CentOS 6.6
export TF_ENABLE_XLA=1
export TF_NEED_VERBS=0
export TF_CUDA_CLANG=0
export TF_DOWNLOAD_CLANG=0
export TF_NEED_MKL=0
export TF_DOWNLOAD_MKL=0
export TF_NEED_MPI=0
export TF_NEED_S3=1
export TF_NEED_KAFKA=1
export TF_NEED_GDR=0
export TF_NEED_OPENCL_SYCL=0
export TF_SET_ANDROID_WORKSPACE=0
export TF_NEED_AWS=0
export TF_NEED_IGNITE=0
export TF_NEED_ROCM=0

# Compiler options
export GCC_HOST_COMPILER_PATH=$(which gcc)

# Here you can edit this variable to set any optimizations you want.
export CC_OPT_FLAGS="-march=native"

if [ "$USE_GPU" -eq "1" ]; then
  # Cuda parameters
  export CUDA_TOOLKIT_PATH=$CUDA_HOME
  export CUDNN_INSTALL_PATH=$CUDA_HOME
  export TF_CUDA_VERSION="$CUDA_VERSION"
  export TF_CUDNN_VERSION="$CUDNN_VERSION"
  export TF_NEED_CUDA=1
  export TF_NEED_TENSORRT=0
  export TF_NCCL_VERSION=$NCCL_VERSION
  export NCCL_INSTALL_PATH=$CUDA_HOME
  export NCCL_INSTALL_PATH=$CUDA_HOME

  # Those two lines are important for the linking step.
  export LD_LIBRARY_PATH="$CUDA_TOOLKIT_PATH/lib64:${LD_LIBRARY_PATH}"
  ldconfig
fi

export flags="--config=opt --copt=-march=silvermont --copt=-mcx16 --copt=-mssse3 --copt=-msse4.1 --copt=-msse4.2 --copt=-mpopcnt --copt=-mno-avx -k"
export tag="silvermont"
export date="20190707"

# Compilation
./configure

if [ "$USE_GPU" -eq "1" ]; then

  bazel build --config=opt \
              --config=cuda \
              --linkopt="-lrt" \
              --linkopt="-lm" \
              --host_linkopt="-lrt" \
              --host_linkopt="-lm" \
              --action_env="LD_LIBRARY_PATH=${LD_LIBRARY_PATH}" \
              //tensorflow/tools/pip_package:build_pip_package

  PACKAGE_NAME=tensorflow-gpu
  SUBFOLDER_NAME="${TF_VERSION_GIT_TAG}-py${PYTHON_VERSION}-cuda${TF_CUDA_VERSION}-cudnn${TF_CUDNN_VERSION}"

else

  bazel build --config=opt \
              --linkopt="-lrt" \
              --linkopt="-lm" \
              --host_linkopt="-lrt" \
              --host_linkopt="-lm" \
              --action_env="LD_LIBRARY_PATH=${LD_LIBRARY_PATH}" \
              //tensorflow/tools/pip_package:build_pip_package

  PACKAGE_NAME=tensorflow
  SUBFOLDER_NAME="${TF_VERSION_GIT_TAG}-py${PYTHON_VERSION}"
fi

mkdir -p "/wheels/$SUBFOLDER_NAME"

bazel-bin/tensorflow/tools/pip_package/build_pip_package "/wheels/$SUBFOLDER_NAME" --project_name "$PACKAGE_NAME"

# Use the following for TF <= 1.8
# bazel-bin/tensorflow/tools/pip_package/build_pip_package "/wheels/$SUBFOLDER_NAME"

# Fix wheel folder permissions
chmod -R 777 /wheels/
