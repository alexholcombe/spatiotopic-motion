from __future__ import print_function
from psychopy import sound, monitors, core, visual, event, data, gui, logging, info
from math import atan, cos, sin, pi, sqrt, pow
import numpy as np
ballStdDev = 0.8
autoLogging=False
scrn=0 #1 means second screen
fullscr=0
widthPix =1024#1024  #monitor width in pixels
heightPix =768#768  #monitor height in pixels
monitorwidth = 40. #28.5 #monitor width in centimeters
viewdist = 57.; #cm
pixelperdegree = widthPix/ (atan(monitorwidth/viewdist) / np.pi*180)
bgColor = [0,0,0] #"gray background"
allowGUI = False
waitBlank = False
units = 'deg'
monitorname = 'mitsubishi' #in psychopy Monitors Center #Holcombe lab monitor
mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#fetch the most recent calib for this monitor
mon.setSizePix( (widthPix,heightPix) )
myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,
                                            screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor
                                            
locationOfProbe= np.array([0,4])  # np.array([[-10,1.5],[0,1.5],[10,1.5]]) #left, centre, right


#Im supposed to use the built-in logging function, should be able to get everything out of that
myMouse = event.Mouse(visible = 'true',win=myWin)

blackDot = visual.ImageStim(myWin,mask='circle',colorSpace='rgb', color = (-1,-1,-1),size=ballStdDev,autoLog=autoLogging, contrast=0.5, opacity = 1.0)
mouseLocationMarker = visual.ImageStim(myWin,mask='circle',colorSpace='rgb', color = (-1,-1,1),size=ballStdDev,autoLog=autoLogging, contrast=0.5, opacity = 1.0)
notClicked = True

cmperpixel = monitorwidth*1.0/widthPix
degpercm = 1.0/cmperpixel/pixelperdegree;  

while notClicked: #collecting response

    blackDot.pos = locationOfProbe
    blackDot.draw()
    
    #handle key presses each frame
    for key in event.getKeys():
        if key in ['escape','q']:
            myWin.close()
            core.quit()
                    
    mouse1, mouse2, mouse3 = myMouse.getPressed()
    mouseX,mouseY = myMouse.getPos()
    mouseLocationMarker.setPos((mouseX,mouseY))
    x = (mouseX) * degpercm #mouse x location relative to center, converted to degrees from pixels
    monitorheight = cmperpixel*heightPix
    y = (mouseY) * degpercm #mouse x location relative to center, converted to degrees from pixels
    if mouse1:
        notClicked = False
        #print 'assumes window spans entire screen of ',monitorwidth,' cm; mouse position apparently in cm when units is set to deg = (',mouseX,',',mouseY,')'  
        #because mouse apparently giving coordinates in cm, I need to convert it to degrees of visual angle because that's what drawing is done in terms of
        distance = sqrt(pow((locationOfProbe[0]-x),2)+pow((locationOfProbe[1]-y),2))
    mouseLocationMarker.draw()
    myWin.flip() #new frame
myWin.close()

print("mouse x,y=","{:.3f}".format(x),",{:.3f}".format(y)," deg")
print("Object was at ",np.round(locationOfProbe,2), " deg")
print("Distance of click from object was",round(distance,3),"deg")
