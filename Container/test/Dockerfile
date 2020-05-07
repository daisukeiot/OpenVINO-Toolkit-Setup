FROM daisukeiot/openvino-container:ubuntu18.04_openvino2020.2.120_cp3.7_test

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

USER openvino
WORKDIR /home/openvino