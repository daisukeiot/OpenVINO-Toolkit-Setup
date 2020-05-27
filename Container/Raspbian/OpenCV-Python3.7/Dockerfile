#
# Build OpenCV with OpenVINO and Python 3.7
#
FROM debian:buster

USER root

ARG OPENVINO_VER=2020.1.023
ARG OPENVINO=l_openvino_toolkit_runtime_raspbian_p_${OPENVINO_VER}
ARG INSTALL_DIR=/opt/intel/openvino
ARG OPENVINO_DOWNLOAD=https://download.01.org/opencv/2020/openvinotoolkit/2020.1/${OPENVINO}.tgz

RUN dpkg --add-architecture armhf && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        git \
        crossbuild-essential-armhf \
        cmake \
        pkg-config \
        wget \
        xz-utils \
        libgtk2.0-dev:armhf \
        libpython-dev:armhf \
        libpython3-dev:armhf \
        python-numpy \
        python3-numpy \
        libgstreamer1.0-dev:armhf \
        libgstreamer-plugins-base1.0-dev:armhf && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

RUN mkdir -p /opt/intel/openvino && \
    wget --no-check-certificate ${OPENVINO_DOWNLOAD} && \ 
    tar xf l_openvino_toolkit_runtime_raspbian_p*.tgz --strip 1 -C ${INSTALL_DIR}

WORKDIR /

RUN rm -r -f /tmp && \
    /bin/bash -c "source $INSTALL_DIR/bin/setupvars.sh -pyver 3.7" && \
    git clone https://github.com/opencv/opencv.git && \
    cd opencv && \
    git checkout tags/4.2.0-openvino && \
    mkdir opencv_build && \
    mkdir opencv && \
    cd opencv_build && \
    cmake -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX="../opencv" \
      -DOPENCV_CONFIG_INSTALL_PATH="cmake" \
      -DCMAKE_TOOLCHAIN_FILE="../platforms/linux/arm-gnueabi.toolchain.cmake" \
      -DWITH_IPP=OFF \
      -DBUILD_TESTS=OFF \
      -DBUILD_PERF_TESTS=OFF \
      -DOPENCV_ENABLE_PKG_CONFIG=ON \
      -DPKG_CONFIG_EXECUTABLE="/usr/bin/arm-linux-gnueabihf-pkg-config" \
      -DPYTHON2_INCLUDE_PATH="/usr/include/python2.7" \
      -DPYTHON2_NUMPY_INCLUDE_DIRS="/usr/local/lib/python2.7/dist-packages/numpy/core/include" \
      -DPYTHON3_INCLUDE_PATH="/usr/include/python3.7" \
      -DPYTHON3_NUMPY_INCLUDE_DIRS="/usr/local/lib/python3.7/dist-packages/numpy/core/include" \
      -DPYTHON3_CVPY_SUFFIX=".cpython-37m-arm-linux-gnueabihf.so" \
      -DENABLE_NEON=ON \
      -DCPU_BASELINE="NEON" \
      -DWITH_INF_ENGINE=ON \
      -DINF_ENGINE_LIB_DIRS="${INSTALL_DIR}/inference_engine/lib/armv7l" \
      -DINF_ENGINE_INCLUDE_DIRS="${INSTALL_DIR}/inference_engine/include" \
      -DCMAKE_FIND_ROOT_PATH="${INSTALL_DIR}" \
      -DENABLE_CXX11=ON .. && \
    make -j4 && make install

WORKDIR /

RUN tar -zcvf opencv.tar.gz /opencv/opencv