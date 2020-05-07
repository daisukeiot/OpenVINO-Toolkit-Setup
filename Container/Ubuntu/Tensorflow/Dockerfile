#
# Pass variables with --build-arg option
# TAG_TF         : A container with Tensorflow Package
# BASE_IMAGE     : Base Image to install Tensorflow
# PYTHON_VERSION : Python version to install Tensorflow for
#

ARG TAG_TF=
ARG TAG_BASE=ubuntu:18.04

FROM ${TAG_TF} as TensorFlow

FROM ${TAG_BASE}

#
# Local variables
#
ARG PYTHON_VERSION=3.7
ARG PYTHON=python${PYTHON_VERSION}

#
# Run as root to install Tensorflow Pacakge
#
USER root
WORKDIR /tmp

#
# Copy Tensorflow Wheel Package
#
COPY --from=TensorFlow /*.whl .

#
# Install Tensorflow Package
#
RUN ${PYTHON} -m pip install ./*.whl && \
    rm -rf /tmp/*

#
# Switch user to openvino and current directory to /home/openvino
#
USER openvino
WORKDIR /home/openvino