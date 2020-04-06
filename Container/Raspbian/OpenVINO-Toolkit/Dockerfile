#
# Pass variables with --build-arg option
# OS_VERSION  : buster or stretch
# MY_REGISTRY : Your Container Registry
# 
# Reference
# https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_raspbian.html
# https://www.intel.com/content/www/us/en/support/articles/000055220/boards-and-kits.html 
# CMake > 3.7.2
# Python 3.5
#
ARG OS_VERSION=buster

#
# Use Base image built in the previous step
#
FROM balenalib/rpi-raspbian:${OS_VERSION}

RUN [ "cross-build-start" ]

#
# Run as root to install OpenVINO Toolkit Runtime
#
USER root

ARG OPENVINO_VER=2020.1.023
ARG OPENVINO=l_openvino_toolkit_runtime_raspbian_p_${OPENVINO_VER}
ARG INSTALL_DIR=/opt/intel/openvino
ARG OPENVINO_DOWNLOAD=https://download.01.org/opencv/2020/openvinotoolkit/2020.1/${OPENVINO}.tgz

RUN apt-get update && apt-get install -y --no-install-recommends \
	apt-utils \
	automake \
	cmake \
	cpio \
	gcc \
	g++ \
	libatlas-base-dev \
	libgtk-3-dev \
	libstdc++6 \
	libtool \
	libusb-1.0.0-dev \
	lsb-release \
	make \
	python3-pip \
	python3-numpy \
	python3-scipy \
	sudo \
	udev \
	unzip \
	vim \
	wget && \
	rm -rf /var/lib/apt/lists/*

#
# Create user `openvino`
#
RUN useradd -ms /bin/bash -G users openvino && \
   chown openvino -R /home/openvino

#
# Use /tmp folder
#
WORKDIR /tmp

#
# Download OpenVINO Toolkit
#
RUN mkdir -p $INSTALL_DIR && \
    cd $INSTALL_DIR && \
	wget -c ${OPENVINO_DOWNLOAD} && \
	tar xf l_openvino_toolkit_runtime_raspbian_p*.tgz --strip 1 -C ${INSTALL_DIR} && \
    echo "source $INSTALL_DIR/bin/setupvars.sh" >> /home/openvino/.bashrc

#
# Add USB Rule
#
RUN sudo usermod -a -G users "$(whoami)" && \
	/bin/bash -c "source $INSTALL_DIR/bin/setupvars.sh && \
	sh $INSTALL_DIR/install_dependencies/install_NCS_udev_rules.sh"

ENV INSTALLDIR ${INSTALL_DIR}

RUN [ "cross-build-end" ]

#
# Set user to openvino and current directory to /home/openvino
#
USER openvino
WORKDIR /home/openvino

ENTRYPOINT []