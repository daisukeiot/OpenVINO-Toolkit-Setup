ARG BASE_TAG

FROM ${BASE_TAG}

#
# Run as root
#
USER root

ENV INTEL_OPENVINO_DIR=/opt/intel/openvino
ENV OPENVINO_OBJECT_DETECTION_PYTHON=1

#
# Install sudo
#
RUN apt-get update && \
    apt install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt

RUN curl -L https://github.com/libusb/libusb/archive/v1.0.22.zip --output v1.0.22.zip && \
    unzip v1.0.22.zip && \
    cd libusb-1.0.22 && \
    ./bootstrap.sh && \
    ./configure --disable-udev --enable-shared && \
    make -j4

RUN apt-get update && \
    apt-get install -y --no-install-recommends libusb-1.0-0-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt/libusb-1.0.22/libusb

RUN /bin/mkdir -p '/usr/local/lib' && \
    /bin/bash ../libtool   --mode=install /usr/bin/install -c   libusb-1.0.la '/usr/local/lib' && \
    /bin/mkdir -p '/usr/local/include/libusb-1.0' && \
    /usr/bin/install -c -m 644 libusb.h '/usr/local/include/libusb-1.0' && \
    /bin/mkdir -p '/usr/local/lib/pkgconfig' && \
    cd  /opt/libusb-1.0.22/ && \
    /usr/bin/install -c -m 644 libusb-1.0.pc '/usr/local/lib/pkgconfig' && \
    ldconfig

WORKDIR /opt

RUN rm -r -f libusb-1.0.22 && \
    rm v1.0.22.zip

RUN python3.6 -m pip install setuptools==41.0.0 && \
    cd ${INTEL_OPENVINO_DIR}/deployment_tools/model_optimizer/install_prerequisites && \
    ./install_prerequisites.sh

WORKDIR /home/openvino
ADD ./Python ./App
ADD ./startapp.sh  /home/openvino
RUN chmod a+x ./startapp.sh

RUN chmod a+w ./App && \
    cd ./App && \
    git clone https://github.com/opencv/open_model_zoo.git && \
    python3.7 -m pip install setuptools==41.0.0 && \
    python3.7 -m pip install -r ./requirements.txt

USER openvino
WORKDIR /home/openvino

EXPOSE 8080

ENTRYPOINT ["bash", "/home/openvino/startapp.sh"]
