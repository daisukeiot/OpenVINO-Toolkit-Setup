FROM debian:buster

USER root

RUN dpkg --add-architecture armhf && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    crossbuild-essential-armhf \
    git \
    wget \
    libusb-1.0-0-dev:armhf \
    libgtk-3-dev:armhf \
    libavcodec-dev:armhf \
    libavformat-dev:armhf \
    libswscale-dev:armhf \
    libgstreamer1.0-dev:armhf \
    libgstreamer-plugins-base1.0-dev:armhf \
    libpython3-dev:armhf \
    python3-pip

RUN pip3 install numpy cython

RUN wget https://www.cmake.org/files/v3.14/cmake-3.14.3.tar.gz && \
    tar xf cmake-3.14.3.tar.gz && \
    (cd cmake-3.14.3 && ./bootstrap --parallel=$(nproc --all) && make --jobs=$(nproc --all) && make install) && \
    rm -rf cmake-3.14.3 cmake-3.14.3.tar.gz

RUN git clone --recursive https://github.com/openvinotoolkit/openvino.git -b 2020.1

WORKDIR /openvino

RUN mkdir build && \
    cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_TOOLCHAIN_FILE="../cmake/arm.toolchain.cmake" \
        -DTHREADS_PTHREAD_ARG="-pthread" \
        -DNO_BOOT=ON \
        -DENABLE_SSE42=OFF \
        -DENABLE_PYTHON=ON \
        -DPYTHON_EXECUTABLE=/usr/bin/python3.7 \
        -DPYTHON_LIBRARY=/usr/lib/arm-linux-gnueabihf/libpython3.7m.so \
        -DPYTHON_INCLUDE_DIR=/usr/include/python3.7 \
        -DTHREADING=SEQ \
        -DENABLE_GNA=OFF .. && make --jobs=$(nproc --all)
