from __future__ import print_function
from psychopy import sound, monitors, core, visual, event, data, gui, logging, info
from math import atan, cos, sin, pi, sqrt, pow
import numpy as np
from psychopy.tools.monitorunittools import cm2pix, cm2deg, deg2cm, deg2pix, pix2cm, pix2deg
#Visualise whether conversion of pix to deg is working, mainly for mouse
#Discussion of conversion here:
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
visualAngleOfMonitor = 2*  ( atan(   (monitorwidth/2) / viewdist  )  /np.pi*180 )
pixPerDeg = widthPix / visualAngleOfMonitor
#pixelperdegree = widthPix/ (atan(monitorwidth/viewdist) / np.pi*180)
bgColor = [0,0,0] #"gray background"
allowGUI = False
waitBlank = False
windowAndMouseUnits = 'deg'
monitorname = 'mitsubishi' #in psychopy Monitors Center #Holcombe lab monitor
mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#fetch the most recent calib for this monitor
mon.setSizePix( (widthPix,heightPix) )
myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=windowAndMouseUnits,color=bgColor,colorSpace='rgb',fullscr=fullscr,
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

blackDot = visual.Circle(myWin,units='deg',radius=ballStdDev)#,autoLog=autoLogging)
blackDot.setFillColor((-1,-1,-1),colorSpace='rgb')
blackDot.setPos(locationBlackDot)
redDot = visual.Circle(myWin,units='deg',radius=ballStdDev)#,autoLog=autoLogging)
redDot.setFillColor((1,-1,-1),colorSpace='rgb')
redDot.setPos((0,0))
yellowDot = visual.Circle(myWin,units='deg',radius=ballStdDev)#,autoLog=autoLogging)
yellowDot.setFillColor((1,1,-1),colorSpace='rgb')
yellowDot.setPos(locationYellowDot)

mouseLocationMarker = visual.Circle(myWin,units=windowAndMouseUnits,radius=ballStdDev)#,autoLog=autoLogging)
mouseLocationMarker.setFillColor((-1,-1,1), colorSpace='rgb')
notClicked = True

degPerPix = 1.0/pixPerDeg
cmPerPix = monitorwidth*1.0/widthPix
degPerCm = degPerPix/cmPerPix
print('degPerPix = ',round(degPerPix,3), ' so with monitor width of ',widthPix,' you are talking ',round(widthPix*degPerPix,2),' deg')
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
                   
    m_x, m_y = myMouse.getPos()  # in the same units as the Window 
#    m_x_pix = m_x*pixPerDeg
#    m_x_pix = m_x*(widthPix*2)
#    m_y_pix = m_y*(heightPix*2)
    if windowAndMouseUnits == 'pix':
        m_x_pix = m_x
        m_y_pix = m_y
        m_x_degAlex = (m_x_pix) * degPerPix #mouse x location relative to center, converted to degrees from pixels
        m_y_degAlex = (m_y_pix) * degPerPix #mouse x location relative to center, converted to degrees from pixels
        m_x_degPp = pix2deg(m_x_pix, mon)
        m_y_degPp = pix2deg(m_y_pix, mon)
    elif windowAndMouseUnits == 'deg':
        m_x_degAlex = m_x_degPp =  m_x
        m_y_degAlex = m_y_degPp = m_y
        m_x_pix = deg2pix(m_x,mon)
        m_y_pix = deg2pix(m_y,mon)
        
    distanceAlex = sqrt(pow((locationBlackDot[0]-m_x_degAlex),2)+pow((locationBlackDot[1]-m_y_degAlex),2))
    distancePp = sqrt(pow((locationBlackDot[0]-m_x_degPp),2)+pow((locationBlackDot[1]-m_y_degPp),2))

    #deg2cm(degrees, monitor[, correctFlat])
    mouseLocationMarker.setPos((m_x, m_y)) #Because mouseLocationMarker is in same units as windowAndMouseUnits, and mouse returns windowAndMouseUnits, this has to work

    mouseLocatnPixelsMsg = 'x=' + str(round(m_x_pix,1)) + ' pixels' + '   y= ' + str(round(m_y_pix,1)) + ' pixels'
    mouseLocatnTextPixels.setText(mouseLocatnPixelsMsg)
    mouseLocatnTextPixels.draw()

    dotLocatnTextMsg = 'x,y=' + str(locationBlackDot) + ' deg,    ('+str( round(deg2pix(locationBlackDot[0],mon),1) )+', '+str( round(deg2pix(locationBlackDot[1],mon),1) )+ ' pixels Pp'
    dotLocatnText.setText(dotLocatnTextMsg)
    dotLocatnText.draw()

    yellowDotLocatnTextMsg=  'x,y=' + str(locationYellowDot) + ' deg,    ('+str( round(deg2pix(locationYellowDot[0],mon),1) )+', '+str( round(deg2pix(locationYellowDot[1],mon),1) )+ ' pixels Pp'
    yellowDotLocatnText.setText(yellowDotLocatnTextMsg)
    yellowDotLocatnText.draw()

    if windowAndMouseUnits=='pix':  #test conversion of pix to deg
        mouseLocatnTextAlex.setText(mouseLocatnTextPixels)
        mouseLocatnMsgAlex = 'Alex dist='+ str(round(distanceAlex,2))+ '   x=' + str(round(m_x_degAlex,2)) + ' y=' + str(round(m_y_degAlex,2)) + ' deg '
        mouseLocatnTextAlex.setText(mouseLocatnMsgAlex)
        mouseLocatnMsgPp =  'Psychopy dist='+ str(round(distancePp,2))+ '   x=' + str(round(m_x_degPp,2)) + ' y=' + str(round(m_y_degPp,2)) + ' deg '
        mouseLocatnTextPp.setText(mouseLocatnMsgPp)
        mouseLocatnTextAlex.draw()
        mouseLocatnTextPp.draw()

    mouseLocationMarker.draw()
    myWin.flip() #new frame
    
    mouse1, mouse2, mouse3 = myMouse.getPressed()
    if mouse1 or mouse2 or mouse3:
        notClicked = False
myWin.close()

print("Alex mouse x,y=","{:.3f}".format(m_x_degAlex),",{:.3f}".format(m_y_degAlex)," deg")
print("Pp mouse x,y=","{:.3f}".format(m_x_degPp),",{:.3f}".format(m_y_degPp)," deg")

print("Object was at ",np.round(locationBlackDot,2), " deg")
print("Alex Distance of click from object was",round(distanceAlex,3),"deg")
