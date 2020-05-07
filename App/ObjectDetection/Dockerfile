ARG BASE_TAG

FROM ${BASE_TAG}

#
# Local variables
#
ARG PYTHON_BIN=python${PYTHON_VERSION}

#
# Run as root
#
USER root

ENV INTEL_OPENVINO_DIR=/opt/intel/openvino
ENV OPENVINO_OBJECT_DETECTION_PYTHON=1

#
# Switch to root to install dependencies
#
USER root
WORKDIR ${INTEL_OPENVINO_DIR}

#
# Install Git
#
RUN apt-get update && \
    apt install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

#
# Install OpenVINO Dependencies
#
RUN cd install_dependencies && \
    ./install_openvino_dependencies.sh

#
# Install dependencies for Model Downloader and Model Optimizer
#
RUN ${PYTHON_BIN} -m pip install -r ${INTEL_OPENVINO_DIR}/deployment_tools/open_model_zoo/tools/downloader/requirements.in && \
    ${PYTHON_BIN} -m pip install -r ${INTEL_OPENVINO_DIR}/deployment_tools/model_optimizer/requirements.txt && \
    apt-get update && \
    apt install -y --no-install-recommends \
        python3-yaml \
        python3-requests && \
    rm -rf /var/lib/apt/lists/* && \
    echo "source ${INTEL_OPENVINO_DIR}/bin/setupvars.sh -pyver ${PYTHON_VERSION}" >> /home/openvino/.bashrc && \
    echo "source ${INTEL_OPENVINO_DIR}/bin/setupvars.sh -pyver ${PYTHON_VERSION}" >> /home/openvino/.bashrc 

WORKDIR /home/openvino
ADD ./Python ./App
ADD ./startapp.sh  /home/openvino
RUN chmod a+x ./startapp.sh

RUN chown openvino -R ./App && \
    cd ./App && \
    git clone https://github.com/opencv/open_model_zoo.git && \
    ${PYTHON_BIN} -m pip install setuptools==41.0.0 && \
    ${PYTHON_BIN} -m pip install -r ./requirements.txt

EXPOSE 8080

USER openvino
WORKDIR /home/openvino

ENTRYPOINT ["bash", "/home/openvino/startapp.sh"]
