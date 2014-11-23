from __future__ import print_function
from psychopy import sound, monitors, core, visual, event, data, gui
from psychopy import logging
import numpy as np
from copy import deepcopy
from math import atan, cos, sin, pi, sqrt, pow
import time, colorsys
import sys, platform, os, StringIO
from pylink import *
from pandas import DataFrame
autopilot = False
quitFinder = False
if quitFinder:
    applescript="\'tell application \"Finder\" to quit\'" #quit Finder.
    shellCmd = 'osascript -e '+applescript
    os.system(shellCmd)

trialClock = core.Clock()

ballStdDev = 0.8
autoLogging = False
participant = 'Hubert'
infoFirst = {'Participant':participant, 'Check refresh etc':False, 'Fullscreen (timing errors if not)': False, 'Screen refresh rate': 60 }
OK = gui.DlgFromDict(dictionary=infoFirst, 
    title='Szinte & Cavanagh spatiotopic apparent motion', 
    order=[ 'Participant','Check refresh etc', 'Fullscreen (timing errors if not)'], 
    tip={'Check refresh etc': 'To confirm refresh rate and that can keep up, at least when drawing a grating'},
    #fixed=['Check refresh etc'])#this attribute can't be changed by the user
    )
if not OK.OK:
    print('User cancelled from dialog box'); core.quit()
participant = infoFirst['Participant']
checkRefreshEtc = infoFirst['Check refresh etc']
fullscr = infoFirst['Fullscreen (timing errors if not)']
refreshRate = infoFirst['Screen refresh rate']
quitFinder = False
if checkRefreshEtc:
    quitFinder = True 
if quitFinder:
    import os
    applescript="\'tell application \"Finder\" to quit\'"
    shellCmd = 'osascript -e '+applescript
    os.system(shellCmd)
respDeadline = 100
if autopilot:
    respDeadline = 0.1
timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime()) 
if os.path.isdir('.'+os.sep+'data'):
    dataDir='data'
else:
    print('"data" directory does not exist, so saving data in present working directory')
    dataDir='.'
fileName = os.path.join(dataDir, participant+'_spatiotopicMotion_'+timeAndDateStr)
dataFile = open(fileName+'.txt', 'w')  # sys.stdout  #StringIO.StringIO()
saveCodeCmd = 'cp \'' + sys.argv[0] + '\' '+ fileName + '.py'
os.system(saveCodeCmd)  #save a copy of the code as it was when that subject was run
logFname = fileName+'.log' 
ppLogF = logging.LogFile(logFname, 
    filemode='w',#if you set this to 'a' it will append instead of overwriting
    level=logging.INFO)#errors, data and warnings will be sent to this logfile 
    
fullscr=0 
scrn=0 #1 means second screen
widthPix =1024#1024  #monitor width in pixels
heightPix =768#768  #monitor height in pixels
monitorwidth = 40. #28.5 #monitor width in centimeters
viewdist = 57.; #cm
pixelperdegree = widthPix/ (atan(monitorwidth/viewdist) / np.pi*180)
bgColor = [0,0,0] #"gray background"
monitorname = 'mitsubishi' #in psychopy Monitors Center
allowGUI = False
waitBlank = False
units = 'deg'

mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#fetch the most recent calib for this monitor
mon.setSizePix( (widthPix,heightPix) )
myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,
                                       colorSpace='rgb',color=bgColor,fullscr=fullscr,screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor
targetDot = visual.ImageStim(myWin,mask='circle',colorSpace='rgb', color = (-1, 1.0, -1), size=ballStdDev,autoLog=autoLogging, contrast=1, opacity = 1.0)
foilDot = visual.ImageStim(myWin,mask='circle',colorSpace='rgb', color = (.8, 0, 1),size=ballStdDev,autoLog=autoLogging, contrast=1, opacity = 1.0)
blackDot = visual.ImageStim(myWin,mask='circle',colorSpace='rgb', color = (-1,-1,-1),size=ballStdDev,autoLog=autoLogging, contrast=0.5, opacity = 1.0)

beforeTrialsText = visual.TextStim(myWin,pos=(0, 0),colorSpace='rgb',color = (-1,-1,-1),alignHoriz='center', alignVert='center', height = 0.05, units='norm',autoLog=autoLogging)
respPromptText = visual.TextStim(myWin,pos=(0, -.3),colorSpace='rgb',color =  (-1,-1,-1),alignHoriz='center', alignVert='center', height = 0.07, units='norm',autoLog=autoLogging)
betweenTrialsText = visual.TextStim(myWin,pos=(0, -.4),colorSpace='rgb',color =  (-1,-1,-1),alignHoriz='center', alignVert='center', units='norm',autoLog=autoLogging)
           
locationOfProbe= np.array([[-10,1.5]])  # np.array([[-10,1.5],[0,1.5],[10,1.5]]) #left, centre, right
#Potential other conditions:[-10,6.5],[0,6.5],[10,6.5],[-10,-3.5],[0,-3.5],[10,-3.5]

stimList=[]
for locus in locationOfProbe: #location of the probe for the trial
    probeLocationY = locus[1]
    for upDown in [-1,1]: #switching between probe moving top to bottom; and bottom to top
      for startLeft in [False,True]: 
        for tilt in [-2,2]: # [-0.875,0,0.875]: #adjusting whether the probe jump is vertical, or slanted
            for jitter in [-0.875,0,0.875]:#shifting each condition slightly from the location to ensure participants dont recognise tilted trials by the location of the initial probe
                probeLocationX = locus[0]+jitter
                stimList.append({'probeX': probeLocationX, 'probeY':probeLocationY, 'startLeft':startLeft, 'upDown': upDown, 'tilt': tilt, 'jitter': jitter})

blockReps = 1
trials = data.TrialHandler(stimList, blockReps)
thisTrial = trials.next()

#durations in frames
initialDur = round(0.1*refreshRate) #target and foil dot without probe for the first 600 ms
probeFirstDisappearance = round(0.5*refreshRate) # probe disappears for 100 ms whilst target and foil dot remain the same
switchCues = round(0.6*refreshRate) # target and foil dots switch positions for 100 ms
probeSecondAppearance = round(0.7*refreshRate) # probe returns on the other side of the horizontal meridian for 400 ms
probeSecondDisappearance = round(1.1*refreshRate) # probe disappears
oneCycleFrames = int( round( probeSecondDisappearance + 0.1*refreshRate ) )
totFrames = oneCycleFrames*3

def oneFrameOfStim(n,targetDotPos,foilDotPos,probePos1,probePos2): #trial stimulus function
    targetDotPosThis = deepcopy(targetDotPos) #dont change starting value 
    foilDotPosThis =  deepcopy(foilDotPos)
    
    twoCycles = oneCycleFrames*2 #First the target dot left->right->left->right to get eye movements in swing of things
    cycleFrame = n % oneCycleFrames
    if cycleFrame <= initialDur:   #show target and foil only, either because first part of trial
        pass #dont draw black dot, dont change positions
    elif initialDur <= cycleFrame < probeFirstDisappearance: #show first position of probe
        if n >= twoCycles: #dont draw probe for first two cycles
            blackDot.pos = (probePos1)
            blackDot.draw()
    elif probeFirstDisappearance <= cycleFrame < switchCues:  #after probe first disappearance, but before target moves
        pass #dont draw black dot, don't change positions
    elif switchCues <= cycleFrame < probeSecondAppearance: #target and foil in exchanged positions
        targetDotPosThis *=-1
        foilDotPosThis *= -1
    elif probeSecondAppearance <= cycleFrame < probeSecondDisappearance: #target and foil, in exchanged positions, probe in new location
        targetDotPosThis *=-1
        foilDotPosThis *=-1
        if n >= twoCycles: #dont draw probe for first two cycles
            blackDot.pos = (probePos2)
            blackDot.draw()
    elif probeSecondDisappearance <= cycleFrame < oneCycleFrames:
        targetDotPosThis *=-1
        foilDotPosThis *= -1
        
    targetDot.pos= (targetDotPosThis)
    foilDot.pos= (foilDotPosThis)
    targetDot.draw()
    foilDot.draw()
    myWin.flip()

print('trialnum\tsubject\tprobeX\tprobeY\tstartLeft\tupDown\tTilt\tJitter\trespFwdBackslash', file=dataFile)

expStop = False
nDone = 0
while nDone < trials.nTotal and not expStop:
    if nDone ==0:
        beforeTrialsText.setText("In this task you are  to look directly at the green dot, wherever it moves on the screen "
                   "Whilst looking at the green dot, you will see a black dot that will either move upwards or downwards during the "
                   "trial. At the end of the trial you are required to identify whether or not the black dot moved in a clockwise "
                   "or anticlockwise direction. Press the right arrow if its trajectory had the tilt of  a forward slash / \n"
                   "and the left arrow if it had the tilt of a backslash \ ")
        respPromptText.setText("anticlockwise \                          clockwise /      ")
        beforeTrialsText.draw()
        respPromptText.draw()
        betweenTrialsText.setText('Press SPACE to continue')
        betweenTrialsText.draw()
        myWin.flip(clearBuffer=True)
        if not autopilot:
            keysPressed = event.waitKeys(maxWait = 120, keyList = ['space','escape'], timeStamped = False)
            if 'escape' in keysPressed:
                print('User cancelled by pressing <escape>'); myWin.close(); core.quit()
        myWin.clearBuffer()

    if thisTrial['startLeft']:
        targetDotPos=np.array([-5,0]) # position of the green and grey stimulus for first half of trials - left to right - this has not been coded in to the data file, may be a good idea to do so
        foilDotPos =np.array([5,0])  
    else: #start on right
        targetDotPos=np.array([5,0])  #position of the green and grey stimulus for second half of trials - right to left
        foilDotPos =np.array([-5,0])
    probePos1= (thisTrial['probeX']+thisTrial['tilt'],      thisTrial['probeY']*thisTrial['upDown'])
    probePos2 =([thisTrial['probeX']-thisTrial['tilt'],     probePos1[1]*-1]) #y of second location is simply vertical reflection of position 1
    
    for n in range(totFrames): #Loop for the trial stimulus
        oneFrameOfStim(n,targetDotPos,foilDotPos,probePos1,probePos2)
    
    keysPressed = event.waitKeys(maxWait = respDeadline, keyList = ['left','right','escape'], timeStamped = False)
    if keysPressed is None:
        keysPressed = ['-99'] #because otherwise testing what's in it gives error
    if autopilot and ('escape' not in keysPressed): #optionally person can press key, like esc to abort
        keysPressed = ['right']
        
    if 'escape' in keysPressed:
            expStop=True
    if not expStop:
        if 'left' in keysPressed: #recoding key presses as 0 (anticlockwise) or 1 (clockwise) for data analysis
            respFwdBackslash = 0
        else:
            respFwdBackslash = 1        
        if nDone==0: #initiate results dataframe
            print(thisTrial)  #deubgON
            df = DataFrame(thisTrial, index=[nDone],
                            columns = ['jitter','probeX','probeY','startLeft','tilt','upDown']) #columns included purely to specify their order
            df['respFwdBackslash'] = respFwdBackslash              
        else: #add this trial
            df= df.append( thisTrial, ignore_index=True ) #ignore because I got no index (rowname)
            df['respFwdBackslash'][nDone] = respFwdBackslash
            print(df)
        #print('startLeft=',thisTrial['startLeft'], 'tilt = ', thisTrial['tilt'], 'respFwdBackslash=',respFwdBackslash)
        #print(df.loc[nDone]) #this is how you pick out a row. Technically, index with value nDone
        #print('trialnum\tsubject\tprobeX\tprobeY\tstartLeft\tupDown\tTilt\tJitter\tDirection\t', file=dataFile)
        #Should be able to print from the dataFrame in csv format
        oneTrialOfData = (str(nDone)+'\t'+participant+'\t'+ "%2.2f\t"%thisTrial['probeX'] + "%2.2f\t"%thisTrial['probeY'] + "%r\t"%thisTrial['startLeft'] +
                                    "%r\t"%thisTrial['upDown'] +  "%r\t"%thisTrial['tilt'] + "%r\t"%thisTrial['jitter']+ "%r"%respFwdBackslash)
        print(oneTrialOfData, file= dataFile)
        if nDone< trials.nTotal-1:
            betweenTrialsText.draw()
            myWin.flip(clearBuffer=True) 
            keysPressedBetweenTrials = event.waitKeys(maxWait = respDeadline, keyList = ['space','escape'], timeStamped = False)
            if keysPressedBetweenTrials is None:
                keysPressedBetweenTrials = ['-99'] #because otherwise testing what's in it gives not-iterable error
            if autopilot and ('escape' not in keysPressedBetweenTrials): # ( keysPressedBetweenTrials is None):
                keysPressedBetweenTrials = ['space']
            if 'escape' in keysPressedBetweenTrials:
                    expStop=True
            thisTrial=trials.next()
            myWin.clearBuffer()
        nDone+=1

dataFile.flush(); logging.flush()
myWin.close()

if expStop:
    print("Experiment stopped because user stopped it.")
else: 
    print("Experiment finished")
if  nDone >0:


    #Use pandas to calculate proportion correct at each level
    #The df.dtypes in my case are  "objects". I don't know what that is and you can't take the mean
    print('df.dtypes=\n',df.dtypes)
    df = df.convert_objects(convert_numeric=True) #convert dtypes from object to numeric
    print('df.dtypes=\n',df.dtypes)
    grouped = df.groupby('tilt')
    ns = grouped.sum() #want n per trial to scale data point size
    ns = list(ns['respFwdBackslash'])
    print('ns per tilt=\n',ns)
    print('df mean at each tilt')
    groupMeans= grouped.mean() #a groupBy object, kind of like a DataFrame but without column names, only an index?
    tiltsTested = list(groupMeans.index)
    print('tiltsTested=',tiltsTested)
    print('groupMeans=\n',groupMeans)
    print("groupMeans['respFwdBackslash']=\n",groupMeans['respFwdBackslash'])
    print("list=\n",list(groupMeans['respFwdBackslash']))
    pRespFB = list(groupMeans['respFwdBackslash'])  
    print(  DataFrame({'tilt': tiltsTested, 'pRespFB': pRespFB, 'n': ns },
                                     columns = ['tilt','n','pRespFB']) #columns included purely to specify their order
             )
    #calculate whether under- or over-correcting
    
    tilt = df.loc[:,'tilt']
    neutralStimIdxs = df.loc[df.loc['tilt']==0]
    print('neutralStimIdxs=',neutralStimIdxs)
    df['underOvercorrected'] = -99
    underOver = (df[neutralStimIdxs,'startLeft']*2-1) * (df[neutralStimIdxs,'respFwdBackslash']*2-1)
    print('underOver=',underOver)
    df[neutralStimIdxs,'underOverCorrected'] = underOver
    print('Of ',nDone,' trials, on ',-99, '% of all trials all targets reported exactly correct.',sep='')