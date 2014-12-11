from __future__ import print_function
from psychopy import sound, monitors, core, visual, event, data, gui, logging, info
import numpy as np
from copy import deepcopy
from math import atan, cos, sin, pi, sqrt, pow
import time, sys, platform, os, StringIO
from pandas import DataFrame
from calcUnderOvercorrect import calcOverCorrected
from plotHelpers import plotPsychometricCurve
dataframeInPsychopy = False
if not dataframeInPsychopy:
    from dataRevisionProposal import saveAsWideText #stopgap measure until DataFrame fully part of psychopy

autopilot = True
quitFinder = False
if quitFinder:
    applescript="\'tell application \"Finder\" to quit\'" #quit Finder.
    shellCmd = 'osascript -e '+applescript
    os.system(shellCmd)
trialClock = core.Clock()
ballStdDev = 0.8
autoLogging = False
participant = 'Hubert'
fullscr=False
refreshRate = 60
infoFirst = {'Participant':participant, 'Check refresh etc':False, 'Fullscreen (timing errors if not)': fullscr, 'Screen refresh rate': refreshRate }
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
demo=False
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
    
scrn=1 #1 means second screen
widthPix =1024#1024  #monitor width in pixels
heightPix =768#768  #monitor height in pixels
monitorwidth = 39. #28.5 #monitor width in centimeters
viewdist = 50.; #cm
pixelperdegree = widthPix/ (atan(monitorwidth/viewdist) / np.pi*180)
bgColor = [0,0,0] #"gray background"
allowGUI = False
waitBlank = False
units = 'deg'
monitorname = 'mitsubishi' #in psychopy Monitors Center #Holcombe lab monitor
mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#fetch the most recent calib for this monitor
mon.setSizePix( (widthPix,heightPix) )
def openMyStimWindow(): #make it a function because have to do it several times, want to be sure is identical each time
    myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=units,color=bgColor,colorSpace='rgb',fullscr=fullscr,
                                            screen=scrn,waitBlanking=waitBlank) #Holcombe lab monitor
    return myWin
myWin = openMyStimWindow()
myWin.recordFrameIntervals = True #required by RunTimeInfo?

refreshMsg2 = ''
refreshRateWrong = False
if not checkRefreshEtc:
    refreshMsg1 = 'REFRESH RATE WAS NOT CHECKED'
else: #checkRefreshEtc
    try:
        runInfo = info.RunTimeInfo(
                # if you specify author and version here, it overrides the automatic detection of __author__ and __version__ in your script
                #author='<your name goes here, plus whatever you like, e.g., your lab or contact info>',
                #version="<your experiment version info>",
                win=myWin,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
                refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
                verbose=True, ## True means report on everything 
                userProcsDetailed=False  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
                                        #seems to require internet access, probably for process lookup
                )
    #print(runInfo)
        logging.info(runInfo)
        print('Finished runInfo- which assesses the refresh and processes of this computer')
        runInfo_failed = False
    except:
        runInfo_failed = True
        refreshMsg1 = ' runInfo call FAILED so dont know refresh rate'
    if not runInfo_failed:
            refreshSDwarningLevel_ms = 3 ##ms
            if runInfo["windowRefreshTimeSD_ms"] > refreshSDwarningLevel_ms:
                print("\nThe variability of the refresh rate is high (SD > %.2f ms)." % (refreshSDwarningLevel_ms))
                ## and here you could prompt the user with suggestions, possibly based on other info:
                if runInfo["windowIsFullScr"]: 
                    print("Your window is full-screen, which is good for timing.")
                    print('Possible issues: internet / wireless? bluetooth? recent startup (not finished)?')
                    if len(runInfo['systemUserProcFlagged']):
                        print('other programs running? (command, process-ID):',info['systemUserProcFlagged'])
                        
            medianHz = 1000./runInfo['windowRefreshTimeMedian_ms']
            refreshMsg1= 'Median frames per second ~='+ str( np.round(medianHz,1) )
            refreshRateTolerancePct = 3
            pctOff = abs( (medianHz-refreshRate) / refreshRate )
            refreshRateWrong =  pctOff > (refreshRateTolerancePct/100.)
            if refreshRateWrong:
                refreshMsg1 += ' BUT'
                refreshMsg1 += ' program assumes ' + str(refreshRate)
                refreshMsg2 =  'which is off by more than' + str(round(refreshRateTolerancePct,0)) + '%!!'
            else:
                refreshMsg1 += ', which is close enough to desired val of ' + str( round(refreshRate,1) )
            myWinRes = myWin.size
            myWin.allowGUI =True
myWin.close() #have to close window to show dialog box

myDlg = gui.Dlg(title="Screen check", pos=(200,400))
myDlg.addText(refreshMsg1, color='Black')
if refreshRateWrong:
    myDlg.addText(refreshMsg2, color='Red')
if refreshRateWrong:
    logging.error(refreshMsg1+refreshMsg2)
else: logging.info(refreshMsg1+refreshMsg2)

if checkRefreshEtc and (not demo) and (myWinRes != [widthPix,heightPix]).any():
    msgWrongResolution = 'Screen apparently NOT the desired resolution of '+ str(widthPix)+'x'+str(heightPix)+ ' pixels!!'
    myDlg.addText(msgWrongResolution, color='Red')
    logging.error(msgWrongResolution)
    print(msgWrongResolution)
myDlg.addText('Note: to abort press ESC at a trials response screen', color=[-1.,1.,-1.]) # color='DimGrey') color names stopped working along the way, for unknown reason
myDlg.show()
if myDlg.OK: #unpack information from dialogue box
    pass
else: 
   print('User cancelled from dialog box.')
   logging.flush()
   core.quit()
if not demo: 
    allowGUI = False
myWin = openMyStimWindow()

targetDot = visual.ImageStim(myWin,mask='circle',colorSpace='rgb', color = (-1, 0.7, -1), size=ballStdDev,autoLog=autoLogging, contrast=1, opacity = 1.0)
foilDot = visual.ImageStim(myWin,mask='circle',colorSpace='rgb', color = (.8, 0, 1),size=ballStdDev,autoLog=autoLogging, contrast=1, opacity = 1.0)
blackDot = visual.ImageStim(myWin,mask='circle',colorSpace='rgb', color = (-1,-1,-1),size=ballStdDev,autoLog=autoLogging, contrast=0.5, opacity = 1.0)

beforeTrialsText = visual.TextStim(myWin,pos=(0, 0),colorSpace='rgb',color = (-1,-1,-1),alignHoriz='center', alignVert='center', height = 0.05, units='norm',autoLog=autoLogging)
respPromptText = visual.TextStim(myWin,pos=(0, -.3),colorSpace='rgb',color =  (-1,-1,-1),alignHoriz='center', alignVert='center', height = 0.07, units='norm',autoLog=autoLogging)
betweenTrialsText = visual.TextStim(myWin,pos=(0, -.4),colorSpace='rgb',color =  (-1,-1,-1),alignHoriz='center', alignVert='center',height=.03,units='norm',autoLog=autoLogging)
NextRemindCountText = visual.TextStim(myWin,pos=(0,-.6),colorSpace='rgb',color= (1,1,1),alignHoriz='center', alignVert='center',height=.05,units='norm',autoLog=autoLogging)

locationOfProbe= np.array([[0,1.5]])  # np.array([[-10,1.5],[0,1.5],[10,1.5]]) #left, centre, right
#Potential other conditions:[-10,6.5],[0,6.5],[10,6.5],[-10,-3.5],[0,-3.5],[10,-3.5]

stimList=[]
for locus in locationOfProbe: #location of the probe for the trial
    probeLocationY = locus[1]
    for upDown in [False,True]: #switching between probe moving top to bottom; and bottom to top
      for startLeft in [False,True]: 
        for tilt in [-.4,0,.4]: # [-0.6,0,0.6]: # # [-0.875,0,0.875]: #adjusting whether the probe jump is vertical, or slanted. Tilt positive means second position to right
            for jitter in [-0.875,0,0.875]:#shifting each condition slightly from the location to ensure participants dont recognise tilted trials by the location of the initial probe
                probeLocationX = locus[0]+jitter
                stimList.append({'probeX': probeLocationX, 'probeY':probeLocationY, 'startLeft':startLeft, 'upDown': upDown, 'tilt': tilt, 'jitter': jitter})

blockReps = 2
trials = data.TrialHandler(stimList, blockReps)
thisTrial = trials.next()

#durations in frames
durWithoutProbe = 0.1
durProbe = 0.4

initialDurS = durWithoutProbe
probeFirstDisappearanceS = initialDurS + durProbe
switchCuesS = probeFirstDisappearanceS+durWithoutProbe
probeSecondAppearanceS = switchCuesS + durWithoutProbe
probeSecondDisappearanceS = probeSecondAppearanceS+durProbe
#convert to frames
initialDur = round(initialDurS*refreshRate) #target and foil dot without probe for the first 600 ms
probeFirstDisappearance = round(probeFirstDisappearanceS*refreshRate) # probe disappears for 100 ms whilst target and foil dot remain the same
switchCues = round(switchCuesS*refreshRate) # target and foil dots switch positions for 100 ms
probeSecondAppearance = round(probeSecondAppearanceS*refreshRate) # probe returns on the other side of the horizontal meridian for 400 ms
probeSecondDisappearance = round(probeSecondDisappearanceS*refreshRate) # probe disappears

oneCycleFrames = int( round( probeSecondDisappearance + durWithoutProbe*refreshRate ) )
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

print('trialnum\tsubject\tprobeX\tprobeY\tstartLeft\tupDown\tTilt\tJitter\trespLeftRight', file=dataFile)

expStop = False
nDone = 0
while nDone < trials.nTotal and not expStop:
    if nDone ==0:
        beforeTrialsText.setText("In this task you are to look directly at the green dot, wherever it moves on the screen. "
                   "Keep looking at the green dot, but attend to the black dot that will either move upwards or downwards during the "
                   "trial. At the end of the trial you are required to identify whether the black dot moved (slightly) to the left "
                   "or the right. Mostly it will have jumped vertically but with a slight left or right offset. "
                   "Press the left arrow for left, \n"
                   "or the right arrow for right ")
        respPromptText.setText("<---- left                            right ---->")
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
        targetDotPos=np.array([-5,0]) #target of saccades starts on left. 
        foilDotPos =np.array([5,0])  
    else: #target starts on right
        targetDotPos=np.array([5,0])  #position of the green and grey stimulus for second half of trials - right to left
        foilDotPos =np.array([-5,0])
    yMultiplier = thisTrial['upDown']
    if not thisTrial['upDown']:
        yMultiplier = -1
    probePos1= [ thisTrial['probeX']-thisTrial['tilt'],      thisTrial['probeY']*yMultiplier ]
    probePos2 =[ thisTrial['probeX']+thisTrial['tilt'],     probePos1[1]*-1 ] #y of second location is simply vertical reflection of position 1
    
    for n in range(totFrames): #Loop for the trial STIMULUS
        oneFrameOfStim(n,targetDotPos,foilDotPos,probePos1,probePos2)
    core.wait(.1)
    respPromptText.setPos([0,-.5]) #low down so doesnt interfere with apparent motion
    respPromptText.draw()
    myWin.flip(clearBuffer=True) 
    keysPressed = event.waitKeys(maxWait = respDeadline, keyList = ['left','right','escape'], timeStamped = False)
    if keysPressed is None:
        keysPressed = ['-99'] #because otherwise testing what's in it gives error
    if autopilot and ('escape' not in keysPressed): #optionally person can press key, like esc to abort
        keysPressed = ['right']
        
    if 'escape' in keysPressed:
            expStop=True
    if not expStop:
        if 'left' in keysPressed: #recoding key presses as 0 (anticlockwise) or 1 (clockwise) for data analysis
            respLeftRight = 0
        else:
            respLeftRight = 1        
        if nDone==0: #initiate results dataframe
            print(thisTrial)  #debugON
            df = DataFrame(thisTrial, index=[nDone],
                            columns = ['jitter','probeX','probeY','startLeft','tilt','upDown']) #columns included purely to specify their order
            df['respLeftRight'] = respLeftRight    
            #trials.addData('respLeftRight', respLeftRight) #switching to using psychopy-native ways of storing, saving data 
            trials.data.add('respLeftRight', respLeftRight) #switching to using psychopy-native ways of storing, saving data 
        else: #add this trial
            df['respLeftRight'] = respLeftRight    
            df= df.append( thisTrial, ignore_index=True ) #ignore because I got no index (rowname)
            df['respLeftRight'][nDone] = respLeftRight
            print(df.loc[nDone-1:nDone]) #print this trial and previous trial, only because theres no way to print object (single record) in wide format
        #print('trialnum\tsubject\tprobeX\tprobeY\tstartLeft\tupDown\tTilt\tJitter\tDirection\t', file=dataFile)
        #Should be able to print from the dataFrame in csv format
        oneTrialOfData = (str(nDone)+'\t'+participant+'\t'+ "%2.2f\t"%thisTrial['probeX'] + "%2.2f\t"%thisTrial['probeY'] + "%r\t"%thisTrial['startLeft'] +
                                    "%r\t"%thisTrial['upDown'] +  "%r\t"%thisTrial['tilt'] + "%r\t"%thisTrial['jitter']+ "%r"%respLeftRight)
        print(oneTrialOfData, file= dataFile)
        if nDone< trials.nTotal-1:
            betweenTrialsText.draw()
            progressMsg = 'Completed trial number ' + str(nDone) + ' (' + str(trials.nTotal) + ' trials in total )'
            NextRemindCountText.setText(progressMsg)
            NextRemindCountText.draw()
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
    fileNamePP = fileName + "_PSYCHOPY"
    if not dataframeInPsychopy:
        dfFromPP = saveAsWideText(trials,fileNamePP)
        print("dfFromPP=\n",dfFromPP)
        print("dfFromPP.head =\n",dfFromPP.head)
        dfFromPP.to_pickle(fileName+"_DataFrame.pickle") #doing this to have a dataframe to test plotDataAndPsychometricCurve with
    else:
        trials.saveAsWideText(fileNamePP) #After this, I can at leisure in a separate file develop code to analyze the data
    fileNamePickle = fileName #.psydat will automatically be appended
    trials.saveAsPickle(fileNamePickle)
    print("psychopy data summary:")
    trials.printAsText(stimOut=['tilt'], #write summary data to screen 
                      dataOut=['respLeftRight_mean','respLeftRight_std'])
    #Use pandas to calculate proportion correct at each level
    #The df.dtypes in my case are  "objects". I don't know what that is and you can't take the mean
    #print('df.dtypes=\n',df.dtypes)
    df = df.convert_objects(convert_numeric=True) #convert dtypes from object to numeric
        
    tilt = df.loc[:,'tilt']
    neutralStimIdxs = df.loc[tilt==0]
    neutralStimIdxs = (tilt==0)
    #print('neutralStimIdxs=\n',neutralStimIdxs)
    #print('neutralStimIdxs.any()=',neutralStimIdxs.any())
    if len(neutralStimIdxs)>1:
      if neutralStimIdxs.any(): #Calculate over/under-correction, which is only interpretable when tilt=0
        forCalculatn = df.loc[neutralStimIdxs, ['tilt','startLeft','upDown','respLeftRight']]
        overCorrected = calcOverCorrected( forCalculatn )
        print('overCorrected=\n',overCorrected)
        df['overCorrected']= np.nan
        df.loc[neutralStimIdxs, 'overCorrected'] = overCorrected
        #print('dataframe with answer added=\n',df) #debug
        #Summarise under over correct
        print('For 0 tilt, overcorrection responses=', round( 100*df['overCorrected'].mean(), 2),
                  '% of ', df['overCorrected'].count(), ' trials', sep='')
        #Calculate mean for each factor level
        zeroTiltOnly = df.loc[neutralStimIdxs,:]
        startLeft = zeroTiltOnly.groupby('startLeft')
        print('Summary of startLeft\n',startLeft.mean())
        upDown= zeroTiltOnly.groupby('upDown')
        print('Summary of upDown\n',upDown.mean())
    tiltGrp= df.groupby('tilt')
    ns = tiltGrp.sum() #want n per trial to scale data point size
    ns = list(ns['respLeftRight'])
    print('Summary of tilt\n',tiltGrp.mean())
   
    #Fit and plot data
    fit = None
    try:
        intensityForCurveFitting = df['tilt']
        resps = df['respLeftRight']
        fit = data.FitWeibull(intensityForCurveFitting, resps, expectedMin=0, sems = 1.0/len(intensityForCurveFitting))
    except:
        print("Fit failed.")
    plotDataAndPsychometricCurve(fit,intensities,resps,descendingPsycho,threshCriterion)

