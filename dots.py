from psychopy import sound, monitors, core, visual, event, data
from psychopy import logging as ppLog 
import numpy as np
from copy import deepcopy
from math import atan, cos, sin, pi, sqrt, pow
import time, colorsys
import sys, platform, os, StringIO
from pylink import *

import os
applescript="\'tell application \"Finder\" to quit\'" #quit Finder.
shellCmd = 'osascript -e '+applescript
os.system(shellCmd)

timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime()) 
subject = 'CF-Practice'
if os.path.isdir('.'+os.sep+'data'):
    dataDir='data'
else:
    print '"data" directory does not exist, so saving data in present working directory'
    dataDir='.'
fileName = dataDir+'/'+subject+'probeDropTask'+timeAndDateStr

dataFile = open(fileName+'.txt', 'w')  # sys.stdout  #StringIO.StringIO()
logF = open(fileName+'.log', 'w')    #StringIO.StringIO()
saveCodeCmd = 'cp \'' + sys.argv[0] + '\' '+ fileName + '.py'
os.system(saveCodeCmd)  #save a copy of the code as it was when that subject was run
logFname = 'logLastRun.log'
ppLogF = ppLog.LogFile(logFname, 
    filemode='w',#if you set this to 'a' it will append instead of overwriting
    level=ppLog.INFO)#errors, data and warnings will be sent to this logfile - CF: have not added any errors or warnings to this program like 
                        #timing blips or anything. So you may want to add that if you want them
trialClock = core.Clock()




ballStdDev = 0.8
autoLogging = False


fullscr=0 
scrn=1 #1 means second s
widthPix =1440#1024  #monitor width in pixels
heightPix =900#768  #monitor height in pixels
monitorwidth = 40. #28.5 #monitor width in centimeters
viewdist = 57.; #cm
pixelperdegree = widthPix/ (atan(monitorwidth/viewdist) / np.pi*180)
bgColor = [1,1,1] #black background
monitorname = 'mitsubishi' #in psychopy Monitors Center
allowGUI = False
waitBlank = False
hz = 100
units = 'deg'

trialDurFramesTotal = int(1.7*hz) #total duration of each trial
initialProbe = 0.6*hz #green and grey dot without probe for the first 600 ms
trialWithProbe = 1.0*hz #probe appears for 400 ms
probeDisappear = 1.1*hz # probe disappears for 100 ms whilst green and grey dot remain the same
switchCues = 1.2*hz # green and grey dots switch positions for 100 ms
probeReturns = 1.6*hz # probe returns on the other side of the horizontal meridian for 400 ms
disappearsAgain = 1.7*hz # probe disappears

mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#fetch the most recent calib for this monitor
mon.setSizePix( (widthPix,heightPix) )
myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,rgb=bgColor,fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor


gaussian1 = visual.ImageStim(myWin,mask='circle',colorSpace='rgb', color = (-1, 1.0, -1), size=ballStdDev,autoLog=autoLogging, contrast=1, opacity = 1.0)
gaussian2 = visual.ImageStim(myWin,mask='circle',colorSpace='rgb', color = (0, 0, 0),size=ballStdDev,autoLog=autoLogging, contrast=1, opacity = 1.0)
gaussian3 = visual.ImageStim(myWin,mask='circle',colorSpace='rgb', color = (-1,-1,-1),size=ballStdDev,autoLog=autoLogging, contrast=0.5, opacity = 1.0)

beforeTrials = visual.TextStim(myWin,pos=(0, 0),rgb = (-1,-1,-1),alignHoriz='center', alignVert='center', height = 0.05, units='norm',autoLog=autoLogging)
betweenTrials = visual.TextStim(myWin,pos=(0, 0),rgb = (-1,-1,-1),alignHoriz='center', alignVert='center', units='norm',autoLog=autoLogging)
           
#while True:
#    gaussian1.pos= (x)
#    gaussian2.pos= (y)
#    gaussian1.draw()
#    gaussian2.draw()
#    myWin.flip()
locationOfProbe= np.array([[-10,1.5],[0,1.5],[10,1.5]]) #Potential other conditions:[-10,6.5],[0,6.5],[10,6.5],[-10,-3.5],[0,-3.5],[10,-3.5]

stimList=[]
for location in locationOfProbe: #location of the probe for the trial
    for shift in [-1,1]: #switching between probe moving top to bottom; and bottom to top
        for tilt in [-0.875,0,0.875]: #adjusting whether the probe jump is vertical, or slanted
            for jitter in [-0.875,0,0.875]:#shifting each condition slightly from the location to ensure participants dont recognise tilted trials by the location of the initial probe
                probeLocation = [location[0]+jitter, location[1]]
                stimList.append({'location': probeLocation, 'topBottom': shift, 'tilt': tilt, 'jitter': jitter})


blockReps = 1
trials = data.TrialHandler(stimList, blockReps)
thisTrial = trials.next()

def oneFrameOfStim(n): #trial stimulus function
    if nDone<=trials.nTotal/2: 
        greenDotPosition=np.array([-5,0]) # position of the green and grey stimulus for first half of trials - left to right - this has not been coded in to the data file, may be a good idea to do so
        greyDotPosition =np.array([5,0])  
    else:
        greenDotPosition=np.array([5,0])  #position of the green and grey stimulus for second half of trials - right to left
        greyDotPosition =np.array([-5,0])
    probePosition1= (thisTrial['location'][0]+thisTrial['tilt'], thisTrial['location'][1]*thisTrial['topBottom'])
    probePosition2 =([thisTrial['location'][0]-thisTrial['tilt'], probePosition1[-1]*-1])
    if n<initialProbe or probeDisappear< n<switchCues:
        gaussian1.pos= (greenDotPosition)
        gaussian2.pos= (greyDotPosition)
        gaussian1.draw()
        gaussian2.draw()
    elif initialProbe<n<trialWithProbe:
        gaussian1.pos= (greenDotPosition)
        gaussian2.pos= (greyDotPosition)
        gaussian3.pos = (probePosition1)
        gaussian1.draw()
        gaussian2.draw()
        gaussian3.draw()
    elif probeDisappear<n<switchCues or probeReturns<n<disappearsAgain:
        greenDotPosition*=-1
        greyDotPosition*=-1
        gaussian1.pos= (greenDotPosition)
        gaussian2.pos= (greyDotPosition)
        gaussian1.draw()
        gaussian2.draw()
    elif switchCues<n<probeReturns:
        greenDotPosition*=-1
        greyDotPosition*=-1
        gaussian1.pos= (greenDotPosition)
        gaussian2.pos= (greyDotPosition)
        gaussian3.pos = (probePosition2)
        gaussian1.draw()
        gaussian2.draw()
        gaussian3.draw()
    myWin.flip()

print >>dataFile, 'trialnum\tsubject\tlocation\ttopBottom\tTilt\tJitter\tDirection\t'
#print >>dataFile2, 'trialnum\tsubject\tlocation\ttopBottom\tTilt\tDirection\t'


nDone = 1
while nDone<= trials.nTotal:
    if nDone ==1:
        beforeTrials.setText("In this task you are required to look at the green dot on the screen. The green dot will switch positions with "
                   "the grey dot on the screen. You are required to look at the green dot directly, wherever it moves on the screen "
                   "Whilst looking at the green dot, you will see a black dot that will either move upwards or downwards during the "
                   "trial. At the end of the trial you are required to identify whether or not the black dot moved in a clockwise "
                   "or anticlockwise direction. Press the right arrow if it appeared to move clockwise, and the left arrow if it "
                   "moved anticlockwise. For the first block of trials, the green dot will always start in the left position and jump "
                   "to the right. Press SPACE when you are ready to begin.")
        beforeTrials.draw()
        myWin.flip(clearBuffer=True) 
        keyPressBetweenTrials = event.waitKeys(maxWait = 120, keyList = ['space'], timeStamped = False)
        myWin.clearBuffer()
    elif nDone == trials.nTotal/2 + 1:
        beforeTrials.setText("""In this next part of the task, the green dot will appear on the right and jump to the left. Press SPACE to continue.""")
        beforeTrials.draw()
        myWin.flip(clearBuffer=True)
        keyPressBetweenTrials = event.waitKeys(maxWait = 120, keyList = ['space'], timeStamped = False)
        myWin.clearBuffer()

    for n in range(trialDurFramesTotal): #Loop for the trial stimulus
        oneFrameOfStim(n)
    keyPress = event.waitKeys(maxWait = 120, keyList = ['left','right'], timeStamped = False) #'down' removed
#    if keyPress == ['down']:
#        keyCode = 0
    if keyPress == ['left']:#recoding key presses as 0 (anticlockwise) or 1 (clockwise) for data analysis
        keyCode = 0
    else:
        keyCode = 1
    print >>dataFile, nDone,'\t',subject,'\t',thisTrial['location'][0],'\t', thisTrial['topBottom'], '\t', thisTrial['tilt'],'\t', thisTrial['jitter'],'\t', keyCode 
#    print >>dataFile2, nDone,'\t',subject,'\t',thisTrial['location'][0],'\t', thisTrial['topBottom'], '\t', thisTrial['tilt'],'\t', keyCode 
    if nDone< trials.nTotal:
        betweenTrials.setText('Press SPACE to continue')
        betweenTrials.draw()
        myWin.flip(clearBuffer=True) 
        keyPressBetweenTrials = event.waitKeys(maxWait = 120, keyList = ['space'], timeStamped = False) 
        thisTrial=trials.next()
        myWin.clearBuffer()
    nDone+=1
    
    



    