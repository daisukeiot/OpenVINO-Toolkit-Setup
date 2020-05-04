# Physical Device Setup

You can run OpenVINO application on your host machine, or you can host OpenVINO containerized application.

Tools and scripts for OpenVINO

- Scripts for physical device
- Scripts for Docker containers

## Physical Device Setup

Verified with :

- UP2 with Myriad X
- Ubuntu 18.04 LTS
- OpenVINO 2020.2.120

### Ubuntu 18.04 LTS

1. Install Ubuntu 18.04 LTS
1. Clone this repo
1. Update UP2 with :

    This will replace kernel for UP2 then reboot the host machine.

    > [!CAUTION]  
    > Do not run this if your host machine is not UP2

    ```bash
    sudo apt update && \
    sudo apt install -y git && \
    git clone https://github.com/daisukeiot/OpenVINO-Toolkit-Setup.git && \
    cd ./OpenVINO-Toolkit-Setup/UP2/ && \
    ./setup1.sh
    ```

1. Upon reboot run 2nd step of setup with :

    This will install UP2 firmware and reboot the host machine.

    > [!CAUTION]  
    > Do not run this if your host machine is not UP2

    ```bash
    cd OpenVINO-Toolkit-Setup\UP2 && \
    ./setup2.sh
    ```

1. Install Tensorflow with AVX turned off

    ```bash
    cd OpenVINO-Toolkit-Setup\UP2 && \
    ./setup3.sh
    ```

1. Upon reboot, install OpenVINO toolkit  
    [Instruction](../App/ObjectDetection/Python/README.md)

1. Install Docker

    If you are planning to run IoT Edge or containerized OpenVINO application, install Docker

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
    sudo reboot now
    ```
