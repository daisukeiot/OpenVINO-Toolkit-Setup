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
