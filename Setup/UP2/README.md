# UP2 Development Environment with Ubuntu 18.04

Verified with :

- UP2 Kernel
- Ubuntu 18.04 LTS
- OpenVINO 2020.2.120
- Python 3.7.5

## Setting up Ubuntu 18.04 LTS

Install Ubuntu 18.04 LTS then install Kernel and other tools for UP2

1. Install Ubuntu 18.04 LTS to UP2

1. Clone this repo

    This will replace kernel for UP2 then reboot the host machine.

    ```bash
    sudo apt update && \
    sudo apt-get install -y git && \
    git clone https://github.com/daisukeiot/OpenVINO-Toolkit-Setup.git
    ```

1. Replace kernel for UP2

    > [!CAUTION]  
    > Do not run this if your host machine is not UP2

    ```bash
    cd ~/OpenVINO-Toolkit-Setup/Setup/UP2 && \
    ./setup1.sh
    ```

1. Upon reboot run 2nd step of setup with :

    This will install UP2 firmware and reboot the host machine.

    > [!CAUTION]  
    > Do not run this if your host machine is not UP2

    ```bash
    cd ~/OpenVINO-Toolkit-Setup/Setup/UP2 && \
    ./setup2.sh
    ```

## Tensorflow without AVX

UP2 runs ATOM which does not support AVX instruction set.  Install Tensorflow without AVX turned on.

> [!WARNING]  
> To avoid complication, install Tensorflow before installing OpenVINO Toolkit

Install Tensorflow with AVX turned off with :

```bash
cd ~/OpenVINO-Toolkit-Setup/Setup/UP2 && \
./setup3.sh
```

## OpenVINO Toolkit

Upon reboot, install OpenVINO toolkit following [Install OpenVINO to Ubuntu](../Ubuntu/README.md)

## Container Runtime Setup

If you are planning to run containerized OpenVINO application, install Docker or Moby :

Install Moby runtime with :

```bash
sudo apt-get install -y curl && \
curl https://packages.microsoft.com/config/ubuntu/18.04/multiarch/prod.list > ./microsoft-prod.list && \
sudo cp ./microsoft-prod.list /etc/apt/sources.list.d/ && \
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg && \
sudo cp ./microsoft.gpg /etc/apt/trusted.gpg.d/ && \
sudo apt-get update && \
sudo apt-get install -y moby-engine && \
sudo apt-get install -y moby-cli && \
sudo usermod -aG docker $USER && \
rm ./microsoft* && \
sudo reboot now
```

If you plan to run IoT Edge, install IoT Edge runtime with :

```bash
sudo apt-get update && \
sudo apt-get install iotedge
```

### Azure IoT Edge Configuration

- [Install the Azure IoT Edge runtime on Debian-based Linux systems](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-install-iot-edge-linux)

## Next Step

[Run Object Detection Python App](../../README.md#running-object-detection-python-app)