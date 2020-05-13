FROM debian:buster

USER root

RUN dpkg --add-architecture armhf && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
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
    libgstreamer-plugins-base1.0-dev:armhf

# Install Inference Engine
RUN wget --no-check-certificate https://download.01.org/opencv/2019/openvinotoolkit/R2/l_openvino_toolkit_runtime_raspbian_p_2019.2.242.tgz && \
    tar -xf l_openvino_toolkit_runtime_raspbian_p_2019.2.242.tgz
