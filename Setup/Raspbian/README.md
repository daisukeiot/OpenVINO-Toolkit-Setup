# Raspberry Pi Development Environment

Verified with :

- Raspbian Buster (2020-02-13-raspbian-buster-lite)
- Python 3.7.5

## Clone the repo

Clone to Raspberry Pi with :

```cmd
cd ~ && \
sudo apt-get update && \
sudo apt-get install -y git && \
git clone https://github.com/daisukeiot/OpenVINO-Toolkit-Setup.git
```

## OpenVINO Toolkit Setup

Run setup script to setup OS and install OpenVINO Toolkit with :

```bash
cd ~/OpenVINO-Toolkit-Setup/Setup/Raspbian && \
./setup.sh
```

> [!NOTE]  
> The script will change hostname to RP-OpenVINO
