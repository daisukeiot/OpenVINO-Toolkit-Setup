# Object Detection app

## Environment

- Ubuntu 18.04
- Python 3.7
- OpenVINO 2020.2.120

## Clone repo

```bash
sudo apt update && \
sudo apt install -y git && \
git clone https://github.com/daisukeiot/OpenVINO-Toolkit-Setup.git && \
cd ./OpenVINO-Toolkit-Setup/Setup/Ubuntu
```

## Ubuntu Setup

Run setup script :

```bash
cd ~/OpenVINO-Toolkit-Setup/Setup/Ubuntu && \
./setup.sh
```

## Container

If you are planning to run IoT Edge or containerized OpenVINO application, install Docker/Moby

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
