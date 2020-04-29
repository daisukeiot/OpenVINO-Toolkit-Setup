ARG BASE_TAG

FROM ${BASE_TAG}

#
# Run as root
#
USER root

ENV INTEL_OPENVINO_DIR=/opt/intel/openvino

#
# Install sudo
#
RUN apt-get update && \
    apt install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install setuptools==41.0.0 && \
    cd ${INTEL_OPENVINO_DIR}/deployment_tools/model_optimizer/install_prerequisites && \
    ./install_prerequisites.sh 

ADD ./Python ./App
ADD ./startapp.sh  /home/openvino && \
    chmod a+x ./startapp.sh

RUN chmod a+w ./App ./App/video ./App/model ./App/ir && \
    cd ./App && \
    git clone https://github.com/opencv/open_model_zoo.git && \
    pip3 install -r ./requirements.txt

USER openvino
WORKDIR /home/openvino

EXPOSE 8080

ENTRYPOINT ["bash", "/home/openvino/startapp.sh"]
