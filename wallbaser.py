import wx, requests, re, ctypes, subprocess, os, Image, random, time, sys

class Wallbaser(wx.Frame):
    #############################
    # User Preferences - Change these to reflect your system and your preferences
    #############################
    # Define the path to the wallpapers folder
    wallpaperFolderPath = 'C:\\Users\\Harrison\\Pictures\\Wallpapers\\'
    # Don't start paused. This can be changed
    paused = False
    # The default number of seconds between wallpaper changes
    secondBetweenImages = 300 # Every 5 minutes
    # The chance (out of 1) of the next wallpaper being a random one from the cache. The higher this number is the greater the chance that the next wallpaper is from the cache is
    randomWallpaperChance = 0.5
    # The default x and y position of the info bar
    xPos = -1600
    yPos = 1060
    # The default width of the info bar
    width = 1600
    height = 20
    # The background and foreground color of the info bar
    foregroundColor = (100,100,0)
    backgroundColor = (0,0,0)

    #############################
    # System Parameters - Do not normally need to be changed #
    #############################
    # Define a variable to hold the current wallpaper's filename. This is needed for when we want to delete the wallpaper
    wallpaperFilename = ""
    # The prefix is the first string in the bar. This is updated with the current countdown time 
    txtPrefix = ""
    # The main string explains the current statue of the downloadr
    txtMain = ""
    # The suffix comes at the end and is customizable.
    txtSuffix = "Wallbaser - Wallpaper Changer by Harrison Jones"
    # Initalize the current coundown timer to the default
    currentSecondCount = secondBetweenImages
    # Placeholder text to explain why the countdown is paused
    pausedReason = "Default Paused Reason"

    ## wxFrame Initaliation
    def __init__(self, parent, title):
        # Define the info bar. No border, no taskbar, and always on top so we can always click on it
        wx.Frame.__init__(self, parent, -1, "Shaped Window",size=(500,500),
                         style =
                           wx.FRAME_SHAPED
                         | wx.BORDER_NONE
                         | wx.FRAME_NO_TASKBAR
                         | wx.STAY_ON_TOP
                         )
        # Position the info bar, define it's width and height, and set it's background color
        self.Move((self.xPos, self.yPos))
        self.SetClientSize( (self.width,self.height) )
        self.SetBackgroundColour(self.backgroundColor)
        
        # Set the info bar to be transparent
        self.SetTransparent( 175 ) 

        # Initalize the timer to tick once a second
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.timer.Start(1000)

        # Bind some mouse events to the functions they perform when clicks
        # Left mouse click changes the wallpaper soon (within a few seconds)
        self.Bind(wx.EVT_LEFT_UP,       self.ChangeWallpaperSoon)
        # Left mouse double click sets the chance of the next wallpaper being a random from the chace to 100% and changes the wallpaper soon
        self.Bind(wx.EVT_LEFT_DCLICK,   self.RandomWallpaper)
        # A middle mouse click removes the current wallpaper and changes the wallpaper soon
        self.Bind(wx.EVT_MIDDLE_UP,  self.RemoveCurrentWallpaper)
        # A right mouse click toggles the paused state of the program
        self.Bind(wx.EVT_RIGHT_UP,   self.TogglePause)

        # Override the default pain event to our own custom one
        self.Bind(wx.EVT_PAINT,         self.OnPaint)

        # Show the info bar
        self.Show()

    def RemoveCurrentWallpaper(self, evt):
        print "Removing wallpaper with filename '" + self.wallpaperFolderPath + self.wallpaperFilename + "'"
        # Tell the OS to remove the current wallpaper
        os.remove(self.wallpaperFolderPath + self.wallpaperFilename) 
        # Set the countdown timer to 1 seconds so the wallpaper will change soon
        self.currentSecondCount = 5

    def ChangeWallpaperSoon(self, evt):
        self.currentSecondCount = 5

    def RandomWallpaper(self, evt):
        self.currentSecondCount = 5
        self.randomWallpaperChance = 1.0

    def SetWallpaper(self,wallpaper):
        print "Setting wallpaper to '" + self.wallpaperFolderPath + wallpaper + "'"
        self.wallpaperFilename = wallpaper
        # Call a python script which changes wallpapers. For some reason attempts to do it directly don't always succeed
        self.run_command('changeWallpaper.py ' + self.wallpaperFolderPath + wallpaper)

    def run_command(self, command):
        p = subprocess.Popen(command, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        return p.communicate()

    def OnTimer(self, evt):
        # If we are paused simple update the info bar to indicate why the program is paused
        if(self.paused):
            self.txtMain = self.pausedReason
        else:
            # If the timer is up reset the timer and change the wallpaper
            if (self.currentSecondCount <= 0):
                self.currentSecondCount = self.secondBetweenImages
                # See if the next wallpaper will be a random one from the cache or not
                if(random.random() < self.randomWallpaperChance):
                    # If so, set the wallpaper to a random one from the cache. Also reset the chance just in case it was set to 100% by a double click
                    rwallpaper = self.rand_wallpaper()
                    self.randomWallpaperChance = 0.5
                    self.SetWallpaper(rwallpaper)
                else:
                    # Otherwise download a new wallpaper and change to it
                    self.ChangeWallpaperNow(None)
            # If the wallpaper is about to change let the user know
            elif (self.currentSecondCount <= 5):
                num = self.num_of_wallpapers()
                self.txtMain = 'Wallpaper Changing [' + str(num) + ' Cached Wallpapers]'
                self.currentSecondCount = self.currentSecondCount - 1
            # Otherwise simply show that we are 'waiting'
            else:
                self.txtMain = 'Waiting'
                self.currentSecondCount = self.currentSecondCount - 1
        # Show the countdown timer
        self.txtPrefix = '[' + str(self.currentSecondCount).zfill(3) + ']'
        self.Refresh()

    def ChangeWallpaperNow(self, evt):
        # Pause the timer so we have plenty of time to download a new wallpaper
        self.paused = True
        self.pausedReason = 'Paused for Wallpaper Downloading'
        # Init a boolean so we can check if we were able to actually change the wallpaper. If not show a random one from the cache
        wallpaperChanged = False
        try:
            # Generate a random number between 1 and the number of wallpapers in the cahce
            num = random.randrange(1, self.num_of_wallpapers())
            # Use the random number to jump to a location in wallbase.cc's toplist index. The current purity is set to 110. The first 1 is to include 'safe' images, the second is to include 'risky' images, and the final 0 is to NOT include 'NSFW' images. Change to 100 for 'safe' images only or 111 for all images on the toplist. The request returns the HTML page for the wallbase.cc toplist.
            r = requests.get('http://wallbase.cc/toplist/index/' + str(num)  + '?section=wallpapers&q=&res_opt=eqeq&res=0x0&thpp=32&purity=110&board=21&aspect=0.00&ts=3d')

            # Scrap the previously obtained HTML looking for wallpapers. 
            regex = re.compile("wallpaper/(.*)\" target")

            # Capture the filenames
            wids = regex.findall(r.text)

            # Go through each filename we found
            for wid in wids:
                # If the filename was found in the cache skip it and go to the next
                if ((os.path.isfile(self.wallpaperFolderPath + wid + '.jpg')) or (os.path.isfile(self.wallpaperFolderPath + wid + '.png'))):
                    pass
                else:
                    # If the filename isn't in the cache we have to check a few places to find the actual location of the wallpaper
                    r = requests.get('http://wallpapers.wallbase.cc/rozne/wallpaper-' + wid + '.jpg', stream=True)
                    # If the return code is 200 that means we have found it. Go ahead and download it
                    if r.status_code == 200:
                        # Open a file in the wallpaper cache and write the found wallpaper to it
                        with open(self.wallpaperFolderPath + wid + '.jpg', 'wb') as f:
                            for chunk in r.iter_content():
                                f.write(chunk)
                        # Update the current wallpaper to the new one
                        self.SetWallpaper(wid + '.jpg')
                        wallpaperChanged = True
                        break
                    else:
                        r = requests.get('http://wallpapers.wallbase.cc/manga-anime/wallpaper-' + wid + '.jpg', stream=True)
                        if r.status_code == 200:
                            with open(self.wallpaperFolderPath + wid + '.jpg', 'wb') as f:
                                for chunk in r.iter_content():
                                    f.write(chunk)
                            self.SetWallpaper(wid + '.jpg')
                            wallpaperChanged = True
                            break
                        else:
                            r = requests.get('http://wallpapers.wallbase.cc/rozne/wallpaper-' + wid + '.png', stream=True)
                            if r.status_code == 200:
                                with open('E:\\t\\' + wid + '.png', 'wb') as f:
                                    for chunk in r.iter_content():
                                        f.write(chunk)
                                im = Image.open(self.wallpaperFolderPath + wid + '.png')
                                im.save(self.wallpaperFolderPath + wid + '.jpg')
                                #print"\t\t\tDeleting old .png"
                                os.remove(self.wallpaperFolderPath + wid + '.png')
                                #print"\t\t\tSetting desktop background to \"" + self.wallpaperFolderPath + wid + ".jpg\""
                                self.SetWallpaper(wid + '.jpg')
                                wallpaperChanged = True
                                break
                            else:
                                r = requests.get('http://wallpapers.wallbase.cc/manga-anime/wallpaper-' + wid + '.png', stream=True)
                                if r.status_code == 200:
                                    with open(self.wallpaperFolderPath + wid + '.png', 'wb') as f:
                                        for chunk in r.iter_content():
                                            f.write(chunk)
                                    im = Image.open(self.wallpaperFolderPath + wid + '.png')
                                    im.save(self.wallpaperFolderPath + wid + '.jpg')
                                    os.remove(self.wallpaperFolderPath + wid + '.png')
                                    self.SetWallpaper(wid + '.jpg')
                                    wallpaperChanged = True
                                    break
        # If there was an error log it
        except Exception, e:
            print "ERROR " + str(e);

        # If we weren't able to change the wallpaper simply display a random one from the cache
        if (wallpaperChanged == False):
            rwallpaper = self.rand_wallpaper()
            self.SetWallpaper(rwallpaper)

        # Resume the timer
        self.paused = False

    # Draw the infobar
    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        dc.SetTextForeground(self.foregroundColor)
        dc.DrawText(self.txtPrefix + ' - ' + self.txtMain + ' - ' + self.txtSuffix,0,0) 

    # Simply close the infobar when we are told to exit
    def OnExit(self, evt):
        self.Close()

    # If we are currently paused then resume, otherwise pause. If pausing let the user know it was done manually
    def TogglePause(self, evt):
        
        if(self.paused):
            self.paused = False
        else:
            self.paused = True
            self.pausedReason = 'Manually Paused'

    # Go through the current cached wallpapers and chosen one at random
    def rand_wallpaper(self):
        from os import listdir
        from os.path import isfile, join
        onlyfiles = [ f for f in listdir(self.wallpaperFolderPath) if isfile(join(self.wallpaperFolderPath,f)) ]
        i = random.randrange(0,len(onlyfiles))
        return onlyfiles[i]

    # Grab the number of wallpapers in the cache
    def num_of_wallpapers(self):
        from os import listdir
        from os.path import isfile, join
        onlyfiles = [ f for f in listdir(self.wallpaperFolderPath) if isfile(join(self.wallpaperFolderPath,f)) ]
        return len(onlyfiles)

if __name__ == '__main__':
    # Remove the old log file
    os.remove("wallbaser.log")
    # Initalize the application to redirect all print statements to the log file 
    app = wx.App(redirect=True,filename="wallbaser.log")
    # Initalize the wxFrame Wallbaser
    Wallbaser(None, title='Wallbaser Wallpaper Changer by Harrison Jones')
    # Start the application
    app.MainLoop()