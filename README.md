# Oculus/Meta Quest Pornhub Helper 

## Tested on Python 3.10.9, might work with other versions too

it Uses YT-DLP to download the Videos and then upload the videos to an FTP server later on. If you are using a VR, I believe you already have a Wifi. You can see youtube tutorials to setup the FTP Servers.

This is a Flask Webserver implementation, unless you have open ports no one else can acccess it.

Access the webserver at - ```<Machine_IP>:5000``` You can change the codes to your needs.

the home page, has a Form to submit pornhub video link, if you add multiple videos it'll add it to queue.

It downloads one video at a time and then upload.

There are some binary files, it is not malicious. However if you don't believe me, it's alright, you can download the binaries from the sources here -

[https://github.com/yt-dlp/yt-dl](https://github.com/yt-dlp/yt-dlp/releases/) # Only need yt-dlp without any extension and put it inside the folder ```./yt-dlp```

[https://github.com/BtbN/FFmpeg-Builds/releases](https://github.com/BtbN/FFmpeg-Builds/releases) # Download the builds, then inside the ```.zip```, there is a ```bin``` folder. Copy all the ```.exe``` files to ```yt-dlp``` folder.

## Only Tested in Windows rn

## for Linux, you can download the Linux vertsion of ffmpeg and yt-dlp

## Any issues? just copy and paste the Error in the new Issue.
