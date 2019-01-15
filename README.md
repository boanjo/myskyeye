# myskyeye
A personal surveillance system written mainly in Python using TensorFlow for object recognition and OpenCV for most frame worker (capture, save, copy, filter, motion detection etc).

In my setup i run the applications on a [Hetzner](https://www.hetzner.com/) bare metal server outside of my premises and have a continuous RTSP stream from the cameras. The application is built mainly of 4 parts:
* One [RTSP streaming application](https://github.com/epkboan/myskyeye/blob/master/cam/README.md) per camera 
* One [Database](https://github.com/epkboan/myskyeye/blob/master/database/README.md) instance
* One [Web Server](https://github.com/epkboan/myskyeye/blob/master/web_app/README.md) instance
* One [MJPG replay application](https://github.com/epkboan/myskyeye/blob/master/cam/README.md) instance

I have chosen to deploy all the applications in Docker containers as it forces applications to have minimal dependencies, easy to migrate between hosts and is wonderful to manage in a clean way.

![1](https://github.com/epkboan/epkboan.github.io/blob/master/myskyeye.png?raw=true "MySkyEye Overview")

If you want really cheap cameras then i recommend [Wanscam bullet HW0043 camera](https://www.ebay.co.uk/itm/WANSCAM-New-HW0043-1-0Megapixel-720P-Outdoor-Wireless-P2P-IR-Cut-IP-Camera-White/252195426824?epid=2255978054&hash=item3ab804d208:g:iHcAAOSw-0xYbRM4:rk:5:pf:1). They give good enough image quality, are easy to manage and seem very stable (I have a few that have been continuously running without any hiccups for a few years. They are really small but you can strip them even further to add you own custom 10wire cable extension or build it into some other casing.
