## Freenove 4WD Smart Car Kit for Raspberry Pi

> A 4WD smart car kit for Raspberry Pi.

<img src='Picture/icon.png' width='30%'/>
<br>
<img src='Picture/icon1.png' width='30%'/>

### Download

* **Use command in console**

	Run following command to download all the files in this repository.

	`git clone https://github.com/Freenove/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi.git`

* **Manually download in browser**

	Click the green "Clone or download" button, then click "Download ZIP" button in the pop-up window.
	Do NOT click the "Open in Desktop" button, it will lead you to install Github software.

> If you meet any difficulties, please contact our support team for help.

### Install
```
cd Code/Server

sudo chmod 777 start.sh

sudo chmod 644 robot.service
mkdir -p ~/.config/systemd/user
cp robot.service ~/.config/systemd/user

systemctl daemon-reload
systemctl --user enable robot.service
```

#### Running PulseAudio as System-Wide Daemon

```
sudo cp /usr/lib/systemd/user/pulseaudio.service /etc/systemd/system
sudo cp /usr/lib/systemd/user/pulseaudio.socket /etc/systemd/system
sudo vim /etc/systemd/system/pulseaudio.service
```

comment the line: `ConditionUser=!root`

```
sudo vim /etc/systemd/system/pulseaudio.service
```

comment the line: `ConditionUser=!root`

sudo systemctl deamon-reload

sudo systemctl --global disable pulseaudio.service pulseaudio.socket
sudo systemctl --system enable pulseaudio.service pulseaudio.socket


### Support

Freenove provides free and quick customer support. Including but not limited to:

* Quality problems of products
* Using Problems of products
* Questions of learning and creation
* Opinions and suggestions
* Ideas and thoughts

Please send an email to:

[support@freenove.com](mailto:support@freenove.com)

We will reply to you within one working day.

### Purchase

Please visit the following page to purchase our products:

http://store.freenove.com

Business customers please contact us through the following email address:

[sale@freenove.com](mailto:sale@freenove.com)

### Copyright

All the files in this repository are released under [Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License](http://creativecommons.org/licenses/by-nc-sa/3.0/).

![markdown](https://i.creativecommons.org/l/by-nc-sa/3.0/88x31.png)

This means you can use them on your own derived works, in part or completely. But NOT for the purpose of commercial use.
You can find a copy of the license in this repository.

Freenove brand and logo are copyright of Freenove Creative Technology Co., Ltd. Can't be used without formal permission.


### About

Freenove is an open-source electronics platform.

Freenove is committed to helping customer quickly realize the creative idea and product prototypes, making it easy to get started for enthusiasts of programing and electronics and launching innovative open source products.

Our services include:

* Robot kits
* Learning kits for Arduino, Raspberry Pi and micro:bit
* Electronic components and modules, tools
* Product customization service

Our code and circuit are open source. You can obtain the details and the latest information through visiting the following web site:

http://www.freenove.com
