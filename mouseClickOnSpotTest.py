from __future__ import print_function
from psychopy import sound, monitors, core, visual, event, data, gui, logging, info
from math import atan, cos, sin, pi, sqrt, pow
import numpy as np
from psychopy.tools.monitorunittools import cm2pix, cm2deg, deg2cm, deg2pix, pix2cm, pix2deg
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
                                            
mouseLocatnTextPixels = visual.TextStim(myWin,pos=(-.6,-.4),colorSpace='rgb',color= (1,1,1),alignHoriz='left', alignVert='center',height=.06,units='norm',autoLog=autoLogging)
mouseLocatnTextAlex = visual.TextStim(myWin,pos=(-.8,-.6),colorSpace='rgb',color= (1,1,1),alignHoriz='left', alignVert='center',height=.06,units='norm',autoLog=autoLogging)
mouseLocatnTextPp = visual.TextStim(myWin,pos=(-.8,-.8),colorSpace='rgb',color= (1,1,1),alignHoriz='left', alignVert='center',height=.06,units='norm',autoLog=autoLogging)

locationOfProbe= np.array([0,4])  # np.array([[-10,1.5],[0,1.5],[10,1.5]]) #left, centre, right

#Im supposed to use the built-in logging function, should be able to get everything out of that
myMouse = event.Mouse(visible = 'true',win=myWin)

blackDot = visual.Circle(myWin,units=units,radius=ballStdDev)#,autoLog=autoLogging)
blackDot.color='black'
blackDot.colorSpace = 'rgb'
blackDot.setFillColor((-1,-1,-1),colorSpace='rgb')

blackDot.setColor(-1,-1,-1)

blackDot.color = (-1,-1,-1)
mouseLocationMarker = visual.Circle(myWin,units='pix',radius=ballStdDev)#,autoLog=autoLogging)
mouseLocationMarker.colorSpace='rgb'
mouseLocationMarker.color = (-1,-1,1)
notClicked = True

cmperpixel = monitorwidth*1.0/widthPix
degpercm = 1.0/cmperpixel/pixelperdegree;  

while notClicked: #collecting response

    blackDot.setPos(locationOfProbe)
    blackDot.draw()
    
    #handle key presses each frame
    for key in event.getKeys():
        if key in ['escape','q']:
            myWin.close()
            core.quit()
                    
    mouse1, mouse2, mouse3 = myMouse.getPressed()
    m_x_pix, m_y_pix = myMouse.getPos()
    m_x_degAlex = (m_x_pix) * degpercm #mouse x location relative to center, converted to degrees from pixels
    m_y_degAlex = (m_y_pix) * degpercm #mouse x location relative to center, converted to degrees from pixels
    m_x_degPp = pix2deg(m_x_pix, mon)
    m_y_degPp = pix2deg(m_y_pix, mon)
    distanceAlex = sqrt(pow((locationOfProbe[0]-m_x_degAlex),2)+pow((locationOfProbe[1]-m_y_degAlex),2))
    distancePp = sqrt(pow((locationOfProbe[0]-m_x_degPp),2)+pow((locationOfProbe[1]-m_y_degPp),2))

    #deg2cm(degrees, monitor[, correctFlat])
    mouseLocationMarker.setPos((m_x_pix, m_y_pix))
    #mouseLocationMarker.setPos((m_x_degPp, m_y_degPp))
    mouseLocatnTextPixels= 'x=' + str(round(m_x_pix,1)) + ' pixels' + '   y= ' + str(round(m_y_pix,1)) + ' pixels'
    mouseLocatnTextAlex.setText(mouseLocatnTextPixels)
    mouseLocatnMsgAlex = 'dist='+ str(round(distanceAlex,2))+ '  mouse x=' + str(round(m_x_degAlex,2)) + ' y=' + str(round(m_y_degAlex,2)) + ' deg Alex'
    mouseLocatnTextAlex.setText(mouseLocatnMsgAlex)
    mouseLocatnMsgPp =  'dist='+ str(round(distancePp,2))+ '  mouse x=' + str(round(m_x_degPp,2)) + ' y=' + str(round(m_y_degPp,2)) + ' deg Psychopy'
    mouseLocatnTextPp.setText(mouseLocatnMsgPp)
    mouseLocatnTextAlex.draw()
    mouseLocatnTextPp.draw()
    if mouse1:
        notClicked = False
        #print 'assumes window spans entire screen of ',monitorwidth,' cm; mouse position apparently in cm when units is set to deg = (',mouseX,',',mouseY,')'  
        #because mouse apparently giving coordinates in cm, I need to convert it to degrees of visual angle because that's what drawing is done in terms of
    mouseLocationMarker.draw()
    myWin.flip() #new frame
myWin.close()

print("mouse x,y=","{:.3f}".format(x),",{:.3f}".format(y)," deg")
print("Object was at ",np.round(locationOfProbe,2), " deg")
print("Distance of click from object was",round(distanceAlex,3),"deg")
