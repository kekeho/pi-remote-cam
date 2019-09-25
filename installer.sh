HOSTNAME=$1
WIFI_PASSWORD=$2
WIFI_COUNTRY=$3

# Set hostname & password
sudo raspi-config noint do_hostname $HOSTNAME
passwd

sudo apt update
sudo apt upgrade -y
sudo apt install -y python3 python3-pip

# Install raspap
sudo raspi-config nonint do_wifi_country $WIFI_COUNTRY  # Set Wi-Fi country as JP
yes y | wget -q https://git.io/voEUQ -O /tmp/raspap && bash /tmp/raspap

# Change Wi-Fi SSID & Password
sudo sed -e "s/raspi-webgui/${HOSTNAME}/g" > /etc/hostapd/hostapd.conf  # SSID
sudo sed -e "s/ChangeMe/${WIFI_PASSWORD}/g" > /etc/hostapd/hostapd.conf  # password

# Clone raspi-remote-cam
cd ~/
git clone https://github.com/kekeho/pi-remote-cam.git
cd pi-remote-cam

pip3 install -r requirements.txt  # Install pyton dependencies
chmod +x piremotecam.py

# Install service
sudo cp pi-remote-cam.service /etc/systemd/system/
sudo systemctl enable pi-remote-cam

# Enable camera module
sudo raspi-config nonint do_camera 0


echo "Finish! Reboot now"
sudo reboot now
