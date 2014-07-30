# Wallbaser #
## What is it? ##
Wallbaser is a simple wallpaper changer which uses wallbase.cc as the source for new wallpapers to download. 

## How Does it Work ##
Every 5 minutes (configurable) wallbaser automatically choser to change the wallpaper from a cached wallpaper (your saved wallpapers) or download a new one. Which is chosen is random but can be weighted on way or another. Wallbaser's interface is a small 'info bar' on the bottom of your screen. It's location and size are configurable. Interfacing with the info bar is done using mouse clicks

### Interfacing ###

A **single left** mouse click sets the timer to 5 seconds so it can be thought of as a "next" action

A **double left** mouse click sets the timer to 5 seconds but also weights the chance of re-using an old wallpaper to 100%

A **single middle** mouse click removes the current wallpaper and sets the timer to 5 seconds (usefull when Wallbaser downloads a wallpaper you don't like)

A **single right** mouse click pauses the timer (useful if you like the current wallpaper or simply don't want it to change)

## Installation ## 
With Python 2.7+ installed, simply download the two required files:

* changeWallpaper.py
* wallbaser.py

Once downloaded place open wallbaser.py in your favorite notepad program and customize the code to fit your system. The only parameters that have to be changed are

* wallpaperFolderPath - this is where your wallpapers will be saved. Make sure you set it to a path of a existing folder
* xPos - this is the x position of the info bar. Experiment around. A safe value it 0 to get you started
* yPos - this is the y poistion of the info bar. Experiment around. A safe value is 15 or 20 to get you started
* width - this should be set to the width of your monitor in pixels

## Running ##
Once you are finished customizing it (everything in the **User Preferences** section in wallbaser.py is customizable) simply run wallbaser.py (you should be able to double click on it if Python is setup correctly)

## Debug ## 
If something goes wrong, close the python window (if it hasn't already) and check the wallbaser.log file in the same directory wallbaser.py is in. If you find a problem please feel free to post the log file as a issue on the Github repo at https://github.com/harrisonhjones/wallbaser/issues