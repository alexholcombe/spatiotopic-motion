from __future__ import print_function
from psychopy import sound, monitors, core, visual, event, data, gui, logging, info
from math import atan, cos, sin, pi, sqrt, pow
import numpy as np
from psychopy.tools.monitorunittools import cm2pix, cm2deg, deg2cm, deg2pix, pix2cm, pix2deg

# https://groups.google.com/forum/#!topic/psychopy-users/HtCMaH70D98
#degFlatPos might be best

ballStdDev = 2
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

locationBlackDot= np.array([0,4])  
locationYellowDot = np.array([0,8])

mouseLocatnTextPixels = visual.TextStim(myWin,pos=(-.6,-.4),colorSpace='rgb',color= (1,1,1),alignHoriz='left', alignVert='center',height=.06,units='norm',autoLog=autoLogging)
mouseLocatnTextAlex = visual.TextStim(myWin,pos=(-.8,-.6),colorSpace='rgb',color= (1,1,1),alignHoriz='left', alignVert='center',height=.06,units='norm',autoLog=autoLogging)
mouseLocatnTextPp = visual.TextStim(myWin,pos=(-.8,-.8),colorSpace='rgb',color= (1,1,1),alignHoriz='left', alignVert='center',height=.06,units='norm',autoLog=autoLogging)
dotLabelPos = locationBlackDot + np.array([1,0])
dotLocatnText = visual.TextStim(myWin,pos=dotLabelPos,colorSpace='rgb',color= (1,1,1),alignHoriz='left', alignVert='center',height=.7,units='deg',autoLog=autoLogging)
yDotLabelPos = locationYellowDot  + np.array([1,0])
yellowDotLocatnText = visual.TextStim(myWin,pos=yDotLabelPos,colorSpace='rgb',color= (1,1,1),alignHoriz='left', alignVert='center',height=.7,units='deg',autoLog=autoLogging)

blackDot = visual.Circle(myWin,units=units,radius=ballStdDev)#,autoLog=autoLogging)
blackDot.setFillColor((-1,-1,-1),colorSpace='rgb')
blackDot.setPos(locationBlackDot)
redDot = visual.Circle(myWin,units=units,radius=ballStdDev)#,autoLog=autoLogging)
redDot.setFillColor((1,-1,-1),colorSpace='rgb')
redDot.setPos((0,0))
yellowDot = visual.Circle(myWin,units=units,radius=ballStdDev)#,autoLog=autoLogging)
yellowDot.setFillColor((1,1,-1),colorSpace='rgb')
yellowDot.setPos(locationYellowDot)

mouseLocationMarker = visual.Circle(myWin,units='deg',radius=ballStdDev)#,autoLog=autoLogging)
mouseLocationMarker.setFillColor((-1,-1,1), colorSpace='rgb')
notClicked = True

cmperpixel = monitorwidth*1.0/widthPix
degpercm = 1.0/cmperpixel/pixelperdegree;  

myMouse = event.Mouse(visible = 'true',win=myWin)
while notClicked: #collecting response

    blackDot.draw()
    yellowDot.draw()
    redDot.draw()
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
    distanceAlex = sqrt(pow((locationBlackDot[0]-m_x_degAlex),2)+pow((locationBlackDot[1]-m_y_degAlex),2))
    distancePp = sqrt(pow((locationBlackDot[0]-m_x_degPp),2)+pow((locationBlackDot[1]-m_y_degPp),2))

    #deg2cm(degrees, monitor[, correctFlat])
    mouseLocationMarker.setPos((m_x_pix, m_y_pix))
    dotLocatnTextMsg = 'x,y=' + str(locationBlackDot) + ' deg,    ('+str( round(deg2pix(locationBlackDot[0],mon),1) )+', '+str( round(deg2pix(locationBlackDot[1],mon),1) )+ ' pixels Pp'
    dotLocatnText.setText(dotLocatnTextMsg)
    yellowDotLocatnTextMsg=  'x,y=' + str(locationYellowDot) + ' deg,    ('+str( round(deg2pix(locationYellowDot[0],mon),1) )+', '+str( round(deg2pix(locationYellowDot[1],mon),1) )+ ' pixels Pp'
    yellowDotLocatnText.setText(yellowDotLocatnTextMsg)
    mouseLocatnPixelsMsg = 'x=' + str(round(m_x_pix,1)) + ' pixels' + '   y= ' + str(round(m_y_pix,1)) + ' pixels'
    mouseLocatnTextPixels.setText(mouseLocatnPixelsMsg)
    mouseLocatnTextAlex.setText(mouseLocatnTextPixels)
    mouseLocatnMsgAlex = 'dist='+ str(round(distanceAlex,2))+ '  mouse x=' + str(round(m_x_degAlex,2)) + ' y=' + str(round(m_y_degAlex,2)) + ' deg Alex'
    mouseLocatnTextAlex.setText(mouseLocatnMsgAlex)
    mouseLocatnMsgPp =  'dist='+ str(round(distancePp,2))+ '  mouse x=' + str(round(m_x_degPp,2)) + ' y=' + str(round(m_y_degPp,2)) + ' deg Psychopy'
    mouseLocatnTextPp.setText(mouseLocatnMsgPp)
    dotLocatnText.draw()
    mouseLocatnTextAlex.draw()
    mouseLocatnTextPp.draw()
    mouseLocatnTextPixels.draw()
    dotLocatnText.draw()
    yellowDotLocatnText.draw()
    if mouse1:
        notClicked = False
        #print 'assumes window spans entire screen of ',monitorwidth,' cm; mouse position apparently in cm when units is set to deg = (',mouseX,',',mouseY,')'  
        #because mouse apparently giving coordinates in cm, I need to convert it to degrees of visual angle because that's what drawing is done in terms of
    mouseLocationMarker.draw()
    myWin.flip() #new frame
myWin.close()

print("mouse x,y=","{:.3f}".format(x),",{:.3f}".format(y)," deg")
print("Object was at ",np.round(locationBlackDot,2), " deg")
print("Distance of click from object was",round(distanceAlex,3),"deg")
