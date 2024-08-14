# GPX route timelapse
Make (sort of) timelapse videos of your gpx route files! 

[Youtube link to an example video](https://www.youtube.com/watch?v=uFagBApJx_A)

## How it works

This combines and creates HTML maps using gpxpy, then captures them using selenium (chrome).

Needs python. Tested only on Windows.

### 1. Put your .gpx files in the 'input' folder. 
  - For a sensible zoom level, it's best to use one town/region for one video.
  - If you're using a workout tracking service that doesn't have a mass gpx export feature, there may be browser scripts that do it for you.
  - [GPS track editor](http://www.gpstrackeditor.com/) is a nice free program to edit .gpx files in case they need tidying up.

### 2. Run **workout_map.py**
  - May be required to (pip) install folium, gpxpy, pillow, selenium

### 3. Image files will be created in the 'output' folder. 
Turn them into a video any way you like.
   - One free and easy way is to use [DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve). From preferences->user->editing select standard transition and still duration (e.g. 15 frames for a 60fps video), then drag the images onto the timeline, and (optionally) add the default transition to each with ctrl+t.
   - You could also use ffmpeg. An 'images.txt' file is automatically created in the output folder. Something like this should work:

     `ffmpeg -r 4 -f concat -safe 0 -i images.txt -r 60 timelapse.mp4`   

### 4. Edit configuration.py
... if you want to adjust the resolution, map position, zoom level, map tileset etc.

---

Have fun! If you have questions, the best way to reach me is [discord](http://discordapp.com/users/244907716231954442).

[Youtube link to a demonstration video](https://www.youtube.com/watch?v=OBF14k_oCPE)

