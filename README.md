# myskyeye
A personal surveillance system written mainly in Python using TensorFlow for object recognition and OpenCV for most frame worker (capture, save, copy, filter, motion detection etc).

In my setup i run the applications on a [Hetzner](https://www.hetzner.com/) bare metal server outside of my premises and have a continuous RTSP stream from the cameras. The application is built mainly of 4 parts:
* One [RTSP streaming application](https://github.com/epkboan/myskyeye/blob/master/cam/README.md) per camera 
* One [Database](https://github.com/epkboan/myskyeye/blob/master/database/README.md) instance
* One [Web Server](https://github.com/epkboan/myskyeye/blob/master/web_app/README.md) instance
* One [MJPG replay application](https://github.com/epkboan/myskyeye/blob/master/cam/README.md) instance

I have chosen to deploy all the applications in Docker containers as it forces applications to have minimal dependencies, easy to migrate between hosts and is wonderful to manage in a clean way.

![1](https://github.com/epkboan/epkboan.github.io/blob/master/myskyeeye.png?raw=true "MySkyEye Overview")

The applications all share a env.list file that sets environment variables that is passed into the docker containers. The MYSQL parameters are needed both from the CAM apps (registration of motion, objects etc), The MariaDB MySql database and the web_app to display the results.

You must edit the env.list file to match your host and ports you want to use. If you implement this all on one server/host then the myhost will be the same but it could also be different hosts. MJPG, LIVE_CAM URL:s should match the hosts where you start these apps/containers and binds the live feed in the web app to the cameras or replay of videos.
'''
MYSQL_HOST=myhost.registred.domain.org
MYSQL_PORT=8999
MYSQL_USER=user
MYSQL_PASSWORD=Password
MYSQL_DATABASE=myskyeye
TZ=Europe/Stockholm
PYTHONUNBUFFERED=0
MJPG_REPLAY_URL=http://myhost.registred.domain.org:9600/
LIVE_CAM_1_URL=http://myhost.registred.domain.org:9601/
LIVE_CAM_2_URL=http://myhost.registred.domain.org:9602/
''' 

The applications should be able to run on a standard quad core desktop but then the CPU load will be relative high. See my Hetzner bare metal server: Intel Core i7-7700 @ 3.60GHz (Quad core with 8 threads) 64GB RAM

![2](https://github.com/epkboan/epkboan.github.io/blob/master/boan_utilization.jpg?raw=true "Resource Utilization")

As you can see above the CPU goes between 45% and 60% depending on the day/night on the cameras (nightvision is less bit/s due to switching to monochrome mode)

It is primarily the object recognition (Tensorflow) that eats CPU. It could be reduced by just using the object recongnition on the parts where motion is detected but currently it works over the whole frame and for every frame (6fps). If you run this on a standard desktop then you could utilize GPU which is great for Tensorflow. But then you will need to install the docker ce version that has GPU support (and you will most likely not be able to use this applications straight off but rather do a fork.
