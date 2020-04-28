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
    apt install -y --no-install-recommends sudo && \
    rm -rf /var/lib/apt/lists/*

RUN usermod -aG sudo openvino && \
    echo "%sudo  ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/nopasswd

RUN cd ${INTEL_OPENVINO_DIR}/install_dependencies && \
    ./install_NCS_udev_rules.sh

USER openvino
WORKDIR /home/openvino

ADD ./Python ./App
ADD ./startapp.sh  /home/openvino

RUN sudo chmod a+w ./App/video && \
    sudo chmod a+w ./App/model &&\
    sudo chmod a+w ./App/ir

RUN pip3 install -r ./App/requirements.txt

EXPOSE 8080

ENTRYPOINT ["bash", "/home/openvino/startapp.sh"]
