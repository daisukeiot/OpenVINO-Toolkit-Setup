#
# Ubuntu Version
#
ARG OS_VERSION=18.04
FROM ubuntu:${OS_VERSION} as base

ARG OS_VERSION=18.04
ARG TF_VERSION=r1.14
ARG PYTHON_VERSION=3.6.9

#
# https://github.com/tensorflow/tensorflow/blob/r1.14/configure.py#L1386
# 0.24.1 ~ 0.26.2
ARG BAZEL_VERSION=0.26.1

ENV LANG C.UTF-8

RUN echo "Ubuntu Version ${OS_VERSION}"

#
# Run as root user
#
USER root
WORKDIR /

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libcurl3-dev \
        libfreetype6-dev \
        libhdf5-serial-dev \
        libzmq3-dev \
        pkg-config \
        rsync \
        software-properties-common \
        sudo \
        unzip \
        zip \
        zlib1g-dev \
        wget \
        virtualenv \
        swig \
        openjdk-8-jdk \
        openjdk-8-jre-headless \
        python3 \
        python3-dev \
        python3-pip  && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

#
# Some TF tools expect a "python" binary
#
RUN ln -s /usr/bin/python3 /usr/local/bin/python

RUN pip3 --no-cache-dir install --upgrade \
    pip \
    setuptools

RUN pip3 --no-cache-dir install \
    six \
    numpy \
    wheel \
    mock 'future>=0.17.1' && \
    pip3 install -U --user keras_applications --no-deps && \
    pip3 install -U --user keras_preprocessing --no-deps

#
# Clone Tensorflow from GIT
#
RUN git clone --depth 1 --branch $TF_VERSION "https://github.com/tensorflow/tensorflow.git"
ENV TF_ROOT=/tensorflow
WORKDIR /tensorflow

COPY ./TensorFlowBashRc /etc/bash.bashrc
RUN chmod a+rwx /etc/bash.bashrc && \
    /etc/bash.bashrc
#
# Install bazel
#
RUN mkdir /bazel && \
    wget -O /bazel/installer.sh "https://github.com/bazelbuild/bazel/releases/download/${BAZEL_VERSION}/bazel-${BAZEL_VERSION}-installer-linux-x86_64.sh" && \
    wget -O /bazel/LICENSE.txt "https://raw.githubusercontent.com/bazelbuild/bazel/master/LICENSE" && \
    chmod +x /bazel/installer.sh && \
    /bazel/installer.sh && \
    rm -f /bazel/installer.sh

#
# Python options
#
ENV CI_BUILD_PYTHON=python \
    PYTHON_BIN_PATH=/usr/bin/python3 \
    PYTHON_LIB_PATH=/usr/local/lib/python3.6/dist-packages \
    PYTHONPATH=${TF_ROOT}/lib \
    PYTHON_ARG=${TF_ROOT}/lib

#
# Compiler Pramaters
#
ENV TF_NEED_CUDA=0 \
    TF_NEED_GCP=0 \
    TF_CUDA_COMPUTE_CAPABILITIES=5.2,3.5 \
    TF_NEED_HDFS=0 \
    TF_NEED_OPENCL=1 \
    TF_NEED_JEMALLOC=1 \
    TF_ENABLE_XLA=1 \
    TF_NEED_VERBS=0 \
    TF_CUDA_CLANG=0 \
    TF_DOWNLOAD_CLANG=0 \
    TF_NEED_MKL=0 \
    TF_DOWNLOAD_MKL=0 \
    TF_NEED_MPI=0 \
    TF_NEED_S3=0 \
    TF_NEED_KAFKA=0 \
    TF_NEED_GDR=0 \
    TF_NEED_OPENCL_SYCL=0 \
    TF_SET_ANDROID_WORKSPACE=0 \
    TF_NEED_AWS=0 \
    TF_NEED_IGNITE=0 \
    TF_NEED_ROCM=0

#
# Compiler options
#
ENV GCC_HOST_COMPILER_PATH=/usr/bin/gcc

#
# Here you can edit this variable to set any optimizations you want.
# Disabled warnings as we are not touching code...
#
ENV CC_OPT_FLAGS="--copt=-march=silvermont --copt=-mcx16 --copt=-mssse3 --copt=-msse4.1 --copt=-msse4.2 --copt=-mpopcnt --copt=-mno-avx \
      --copt=-Wno-maybe-uninitialized \
      --copt=-Wno-unknown-pragmas \
      --copt=-Wno-sign-compare \
      --copt=-Wno-return-type \
      --copt=-Wno-strict-aliasing \
      --copt=-Wno-comment \
      --copt=-Wno-unused-function \
      --copt=-Wno-un"

ENV tag="silvermont"

RUN ./configure

RUN  bazel build -c opt ${CC_OPT_FLAGS} \
                 --linkopt="-lrt" \
                 --linkopt="-lm" \
                 --host_linkopt="-lrt" \
                 --host_linkopt="-lm" \
                 --action_env="LD_LIBRARY_PATH=${LD_LIBRARY_PATH}" \
                 //tensorflow/tools/pip_package:build_pip_package

ARG PACKAGE_NAME=tensorflow-atom
ARG SUBFOLDER_NAME="${TF_VERSION}-py${PYTHON_VERSION}"

RUN mkdir -p "/wheels/${SUBFOLDER_NAME}" && \
    bazel-bin/tensorflow/tools/pip_package/build_pip_package "/wheels/${SUBFOLDER_NAME}" --project_name "${PACKAGE_NAME}" && \
    chmod -R 777 /wheels/