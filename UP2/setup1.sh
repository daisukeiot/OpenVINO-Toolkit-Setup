sudo apt-get update && \
sudo add-apt-repository ppa:ubilinux/up && \
sudo apt update && \
sudo apt-get autoremove -y --purge 'linux-.*generic' && \
sudo apt-get install -y linux-image-generic-hwe-18.04-upboard && \
sudo apt dist-upgrade -y && \
sudo reboot
