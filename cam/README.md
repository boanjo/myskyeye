# My Sky Eye Camera 
For every camera you want in the system you start a docker instance which you parameterize with the env.list and some additional properties when you create the container. When you have updated the ../env.list and the docker.txt file you can do "source docker.txt" or you can execute the commands one by one or copy and paste the whole content into a command shell.

The Container is based on the tensorflow (ubuntu 16.10) container and is extended with:
* Google Protobuf needed for the tensorflow/research/object_recognition  
* OpenCV for most frame ralated operations
* Some python (2.7) additions 

I have configured each camera to produce 6fps @ 720p which for my case is a good combination of bandwidth and good enough resolution and video flow. The rtsp.py reads the RTSP_URL it has been configured for and puts the frame in a out queue towards the utils/frame_worker.py it then checks it's in queue to see if there are any ready frames ready to be written to video file. The frame only works per frame and motion is detected by filtering every frame and comparing it with previous frame. It also looks for objects using tensorflow and annotates the frame for motion and objects. It also calculates a weight for a frame that is the most suitable as a "mug shot" of who are on the video sequence with criterias like:
* Max persons in the frame
* Biggest closeup
* Centered a bit to the left (change if you want other position)
* Person is completely within the top of the frame (i.e. really close person is not missing it's head :-))

Every time motion is detected a timer is restarted of 10 sec and recording is started. If motion is detected in less than 5 frames during the recoring period then the movie is thrown. That means if there is only one frame with motion every 9 secods that occurs 6 times it will create a video of 5*9+10=55sec   

Each camera produces two live feeds that can be viewed in realtime. One for just the video and one for the motion/object detection and with a histogram with statistics how many milliseconds each frame takes to process.

![1](https://github.com/epkboan/epkboan.github.io/blob/master/myskyeye_motion_detection.png?raw=true "MySkyEye Motion Detection")


This camera solution is not really intended to cover all situations and to use as is. Please feel free to change to suit your needs (exclude areas etc)   

If you want really cheap cameras then i recommend [Wanscam bullet camera (HW0043)](https://www.ebay.co.uk/itm/WANSCAM-New-HW0043-1-0Megapixel-720P-Outdoor-Wireless-P2P-IR-Cut-IP-Camera-White/252195426824?epid=2255978054&hash=item3ab804d208:g:iHcAAOSw-0xYbRM4:rk:5:pf:1). They give good enough image quality, are easy to manage and seem very stable (I have a few that have been continuously running without any hiccups for a few years. They are really small but you can strip them even further to add you own custom 10wire cable extension or build it into some other casing.

