from __future__ import print_function
from psychopy import sound, monitors, core, visual, event, data, gui, logging, info
import numpy as np
from copy import deepcopy
from math import atan, cos, sin, pi, sqrt, pow
import time, sys, platform, os, StringIO
from pandas import DataFrame
from calcUnderOvercorrect import calcOverCorrected
dirOrLocalize = True
autopilot = False
quitFinder = False
if quitFinder:
    applescript="\'tell application \"Finder\" to quit\'" #quit Finder.
    shellCmd = 'osascript -e '+applescript
    os.system(shellCmd)
respClock = core.Clock(); myClock = core.Clock(); 
afterimageDurClock = core.Clock()
refreshRate = 60
ballStdDev = 0.8
autoLogging = False
participant = 'Hubert'
fullscr=True
infoFirst = {'Participant':participant, 'Check refresh etc':False, 'Fullscreen (timing errors if not)': fullscr, 'Screen refresh rate':refreshRate }
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
    
scrn=0 #1 means second screen
widthPix =1024#1024  #monitor width in pixels
heightPix =768#768  #monitor height in pixels
monitorwidth = 40. #28.5 #monitor width in centimeters
viewdist = 57.; #cm
pixelperdegree = widthPix/ (atan(monitorwidth/viewdist) / np.pi*180)
bgColor = [0,0,0] #"gray background"
allowGUI = False
waitBlank = False
windowAndMouseUnits = 'deg'
monitorname = 'mitsubishi' #in psychopy Monitors Center #Holcombe lab monitor
mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#fetch the most recent calib for this monitor
mon.setSizePix( (widthPix,heightPix) )
def openMyStimWindow(): #make it a function because have to do it several times, want to be sure is identical each time
    myWin = visual.Window(monitor=mon,size=(widthPix,heightPix),allowGUI=allowGUI,units=windowAndMouseUnits,color=bgColor,colorSpace='rgb',fullscr=fullscr,
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

targetDot = visual.ImageStim(myWin,mask='circle',colorSpace='rgb', color = (-1, 1.0, -1), size=ballStdDev,autoLog=autoLogging, contrast=1, opacity = 1.0)
foilDot = visual.ImageStim(myWin,mask='circle',colorSpace='rgb', color = (.8, 0, 1),size=ballStdDev,autoLog=autoLogging, contrast=1, opacity = 1.0)
blackDot = visual.ImageStim(myWin,mask='circle',colorSpace='rgb', color = (-1,-1,-1),size=ballStdDev,autoLog=autoLogging, contrast=0.5, opacity = 1.0)
mouseLocationMarker = visual.Circle(myWin,units=windowAndMouseUnits,radius=ballStdDev/2.)#,autoLog=autoLogging)
mouseLocationMarker.setFillColor((-.5,-.5,-.5), colorSpace='rgb')
clickContinueArea = visual.Rect(myWin,units='norm',width=.8,height=.3,fillColor=(-.6,-.6,0),autoLog=autoLogging)
clickContinueArea.setPos((-1,1))
mouseLocationMarker.setFillColor((-.5,-.5,-.5), colorSpace='rgb')

beforeFirstTrialText = visual.TextStim(myWin,pos=(.2, .95),colorSpace='rgb',color = (-1,-1,-1),alignHoriz='center', alignVert='top', height = 0.05, units='norm',autoLog=autoLogging)
respPromptText = visual.TextStim(myWin,pos=(0, -.3),colorSpace='rgb',color =  (-1,-1,-1),alignHoriz='center', alignVert='center', height = 0.07, units='norm',autoLog=autoLogging)
betweenTrialsText = visual.TextStim(myWin,pos=(0, -.4),colorSpace='rgb',color =  (-1,-1,-1),alignHoriz='center', alignVert='center',height=.03,units='norm',autoLog=autoLogging)
nextRemindCountText = visual.TextStim(myWin,pos=(-.95,.95),colorSpace='rgb',color= (1,1,1),alignHoriz='left', alignVert='top',height=.03,units='norm',autoLog=autoLogging)

locationOfProbe= np.array([[0,1.5]])  # np.array([[-10,1.5],[0,1.5],[10,1.5]]) #left, centre, right
#Potential other conditions:[-10,6.5],[0,6.5],[10,6.5],[-10,-3.5],[0,-3.5],[10,-3.5]
stimList=[]
for locus in locationOfProbe: #location of the probe for the trial
    probeLocationY = locus[1]
    for upDown in [False,True]: #switching between probe moving top to bottom; and bottom to top
      for startLeft in [False,True]: 
        tilts = [-2,0,2]
        if dirOrLocalize:
            tilts = [0]
        for tilt in tilts: # [-2,0,2]: # [-0.875,0,0.875]: #adjusting whether the probe jump is vertical, or slanted. Tilt positive means second position to right
                probeLocationX = locus[0]
                stimList.append({'probeX': probeLocationX, 'probeY':probeLocationY, 'startLeft':startLeft, 'upDown': upDown, 'tilt': tilt})

blockReps = 3
trials = data.TrialHandler(stimList, blockReps)
thisTrial = trials.next()

previewCycles = 0
normalCycles = 1
#durations in frames
initialDur = round(0.2*refreshRate) #target and foil dot without probe
probeFirstDisappearance = round(1.2*refreshRate) # probe disappears whilst target and foil dot remain the same
switchCues = round(1.1*refreshRate) # target and foil dots switch positions

probeSecondAppearance = 9999 # probe returns on the other side of the horizontal meridian for 400 ms
probeSecondDisappearance = 9999 # probe disappears
oneCycleFrames = int( round( 2*switchCues  ) )
totFrames = oneCycleFrames*normalCycles

def oneFrameOfStim(n,nWhenAfterimage,finished,targetDotPos,foilDotPos,probePos1,probePos2): #trial stimulus function
    targetDotPosThis = deepcopy(targetDotPos) #dont change starting value 
    foilDotPosThis =  deepcopy(foilDotPos)
    
    #previewFrames = previewCycles*oneCycleFrames #First the target dot left->right->left->right to get eye movements in swing of things
    #cycleFrame = n % oneCycleFrames

    #After he presses key, jump so move eyes
    if nWhenAfterimage <= n: #target and foil in exchanged positions
        targetDotPosThis *=-1
        foilDotPosThis *= -1
    targetDot.pos= (targetDotPosThis)
    foilDot.pos= (foilDotPosThis)
    if n> nWhenAfterimage+5:
        finished = True #time to start waiting for mouse click to record response
    
    if n <= initialDur:   #show target and foil only, because first part of trial
        pass #dont draw black dot, dont change positions
    elif initialDur <= n < probeFirstDisappearance: #show first position of probe
        #if n >= previewFrames: #dont draw probe for first two cycles
        blackDot.pos = (probePos1)
        blackDot.draw()
    else:
        if nWhenAfterimage == 9999: #need to wait until person presses key to indicate afterimage has built up
            event.clearEvents() #clear keypresses and mouse clicks
            waitingForPress = True
            waitStartN = n
            while waitingForPress and ( (n-waitStartN)/refreshRate < respDeadline ):
                blackDot.draw()
                targetDot.draw()
                foilDot.draw()
                myWin.flip()
                n+=1
                keysPressed = event.getKeys()
                if 'space' in keysPressed:
                    waitingForPress = False
                    nWhenAfterimage = n
                    afterimageDurClock.reset()
            if autopilot:
                nWhenAfterimage =0

#    if probeSecondAppearance <= cycleFrame < probeSecondDisappearance: #probe in new location
#        if n >= previewFrames: #dont draw probe for first two cycles
#            blackDot.pos = (probePos2)
#            blackDot.draw()
            
    targetDot.draw()
    foilDot.draw()
    myWin.flip()
    return n, nWhenAfterimage, finished

if dirOrLocalize:
    myMouse = event.Mouse(visible = 'False',win=myWin)
    header = 'trialnum\tsubject\tprobeX\tprobeY\tprobePos1X\tprobePos1Y\tstartLeft\tupDown\ttilt\tjitter\trespX\trespY\tdX\tdY\tafterimageGenesis'
else:
    header = 'trialnum\tsubject\tprobeX\tprobeY\tprobePos1X\tprobePos1Y\tstartLeft\tupDown\ttilt\tjitter\trespLeftRight'
print(header, file=dataFile)

def collectResponse(expStop, dirOrLocalize, stuffToDrawOnRespScreen):
    #if dirOrLocalize True, that means participant must click on a location, not report direction of motion
    afterimageDur = -999
    if dirOrLocalize: #collect mouse click
        waitingForClick = True
        mouseMovedYet = False
        myMouse.getRel() #resets relative to can detect first time mouse moves, and only then draw the marker
        while waitingForClick and respClock.getTime() < respDeadline:
            if (myMouse.getRel()).any():
                mouseMovedYet = True
            m_x, m_y = myMouse.getPos()  # in the same units as the Window 
            mouseLocationMarker.setPos((m_x, m_y)) #Because mouseLocationMarker is in same units as windowAndMouseUnits, and mouse returns windowAndMouseUnits, this has to work
            mouse1, mouse2, mouse3 = myMouse.getPressed()
            if mouse1 or mouse2 or mouse3:
                waitingForClick = False
                afterimageDur = afterimageDurClock.getTime()
                print('afterimageDur=',afterimageDur)
            keysPressed = event.getKeys()
            if 'escape' in keysPressed:
                expStop = True
            if mouseMovedYet:
                mouseLocationMarker.draw() #dont draw marker until mouse moves for the first time
            for x in stuffToDrawOnRespScreen:
                x.draw()
            myWin.flip()
        if expStop or waitingForClick: #person never responded, but timed out. Presumably because of autopilot or hit escape
            m_x = 0.0
            m_y = 0.0
        return (expStop, (m_x, m_y), afterimageDur)
    else: #not dirOrLocalize, so report direction with arrow key
        keysPressed = event.waitKeys(maxWait = respDeadline, keyList = ['left','right','escape'], timeStamped = False)
        if keysPressed is None:
            keysPressed = ['-99'] #because otherwise testing what's in it gives error
        if autopilot and ('escape' not in keysPressed): #optionally person can press key, like esc to abort
            keysPressed = ['right']
        if 'escape' in keysPressed:
                expStop=True
        if 'left' in keysPressed: #recoding key presses as 0 (anticlockwise) or 1 (clockwise) for data analysis
                respLeftRight = 0
        else:
                respLeftRight = 1
        resp = respLeftRight
    return (expStop, resp, afterimageDur)


if dirOrLocalize:
    respPromptText.setText("")
    instructns = ("During a trial, follow the green dot with your eyes."
               "Always look at the green dot, but attend to the black dot that appears. "
               "At the end of the trial please click on where you see the afterimage of the dot. ")
else:
    instructns = ("During a trial, follow the green dot with your eyes. "
               "Always look at the green dot, but attend to the black dot that will either move upwards or downwards during the "
               "trial. At the end of the trial you are required to identify whether the black dot moved (slightly) to the left "
               "or the right. Mostly it will have jumped vertically but with a slight left or right offset. "
               "Press the left arrow for left, \n"
               "or the right arrow for right ")
    respPromptText.setText("<---- left                            right ---->")
beforeFirstTrialText.setText(instructns)

def waitBeforeTrial(nDone,respDeadline,expStop,stuffToDrawOnRespScreen):
    #displayDraw is a function instance to call to draw what want to between trials
    if dirOrLocalize:
        betweenTrialsText.setText('CLICK in blue area to continue')
        clickContinueArea.draw()
    else:
        betweenTrialsText.setText('Press SPACE to continue')
    progressMsg = 'Completed ' + str(nDone) + ' of ' + str(trials.nTotal) + ' trials'
    nextRemindCountText.setText(progressMsg)
    myClock.reset();
    if dirOrLocalize:
        betweenTrialsText.setText('CLICK in blue area to continue')
        waitingForClick = True
        while waitingForClick and respClock.getTime() < respDeadline:
            m_x, m_y = myMouse.getPos()  # in the same units as the Window 
            mouseLocationMarker.setPos((m_x, m_y)) #Because mouseLocationMarker is in same units as windowAndMouseUnits, and mouse returns windowAndMouseUnits, this has to work
            mouse1, mouse2, mouse3 = myMouse.getPressed()
            if myMouse.isPressedIn(clickContinueArea):
                waitingForClick = False
            if waitingForClick and (mouse1 or mouse2 or mouse3):
               myWin.flip(); myWin.flip() #flicker everything to tell user registered your click but it's in wrong place
            keysPressed = event.getKeys()
            if 'escape' in keysPressed:
                expStop = True
            for x in stuffToDrawOnRespScreen:
                x.draw()
            betweenTrialsText.setText('CLICK in blue area to continue')
            if nDone==0:
                beforeFirstTrialText.draw()
            clickContinueArea.draw()
            mouseLocationMarker.draw()
            betweenTrialsText.draw()
            nextRemindCountText.draw()
            myWin.flip()
    if not expStop and not waitingForClick: #person never responded, but timed out. Presumably because of autopilot or hit escape
        waitingForPressBetweenTrials = True
        betweenTrialsText.setText('While looking at the green dot, press SPACE to continue')
        while waitingForPressBetweenTrials and myClock.getTime() < respDeadline:
            if nDone==0:
                beforeFirstTrialText.draw()
            respPromptText.draw()
            betweenTrialsText.draw()
            for x in stuffToDrawOnRespScreen:
                x.draw()
            myWin.flip()
            for key in event.getKeys():       #check if pressed abort-type key
                  if key in ['escape']:
                      expStop = True; waitingForPressBetweenTrials=False
                  if key in ['space']:
                      waitingForPressBetweenTrials=False
    return expStop
#end waiting between trials

expStop = False
nDone = 0
while nDone < trials.nTotal and not expStop:
    if thisTrial['startLeft']:
        targetDotPos=np.array([-5,0]) #target of saccades starts on left. 
        foilDotPos =np.array([5,0])  
    else: #target starts on right
        targetDotPos=np.array([5,0])  #position of the green and grey stimulus for second half of trials - right to left
        foilDotPos =np.array([-5,0])
    yMultiplier = thisTrial['upDown']
    if not thisTrial['upDown']:
        yMultiplier = -1
    jitter = np.random.uniform(-2,2)
    probePos1= [ thisTrial['probeX']+jitter-thisTrial['tilt'],      thisTrial['probeY']*yMultiplier ]
    probePos2 =[ thisTrial['probeX']+jitter+thisTrial['tilt'],     probePos1[1]*-1 ] #y of second location is simply vertical reflection of position 1
    targetDot.setPos(targetDotPos)
    foilDot.setPos(foilDotPos)
    expStop = waitBeforeTrial(nDone, respDeadline, expStop, stuffToDrawOnRespScreen=(targetDot,foilDot)) #show first frame over and over
    nWhenAfterimage = 9999 #record nWhenAfterImage starts
    finished = False
    n=0
    while not finished: #Loop for the trial STIMULUS
        n, nWhenAfterimage, finished = oneFrameOfStim(n,nWhenAfterimage,finished, targetDotPos,foilDotPos,probePos1,probePos2)
        n +=1
    afterimageGenesis = (nWhenAfterimage - probeFirstDisappearance) / refreshRate
    event.clearEvents() #clear keypresses and mouse clicks
    respPromptText.setPos([0,-.5]) #low down so doesnt interfere with apparent motion
    respPromptText.draw()
    targetDot.draw()
    foilDot.draw()
    myWin.flip()
    #myMouse.setPos((-5,-2)) #setPos only works for pygame window, not pyglet that psychopy using now
    #myMouse = event.Mouse(visible = 'False',win=myWin)
    #myMouse.setVisible(True)
    expStop,resp,afterimageDur = collectResponse(expStop, dirOrLocalize, stuffToDrawOnRespScreen=(targetDot,foilDot,respPromptText))
    #myMouse = event.Mouse(visible = 'False',win=myWin)
    #myMouse.setVisible(False)
    if not expStop:
        if nDone==0: #initiate results dataframe
            print(thisTrial)  #debugON
            df = DataFrame(thisTrial, index=[nDone],
                            columns = ['probeX','probeY','startLeft','tilt','upDown']) #columns included purely to specify their order
            df['jitter'] = jitter
            if dirOrLocalize:
                df['respX'] = resp[0]
                df['respY'] = resp[1]
                df['dx'] = resp[0] - probePos1[0]
                df['dy'] = resp[1] - probePos1[1]
                df['afterimageGenesis'] = afterimageGenesis 
                df['afterimageDur'] = afterimageDur
            else:
                df['respLeftRight'] = resp
        else: #Not first trial. Add this trial
            df= df.append( thisTrial, ignore_index=True ) #ignore because I got no index (rowname)
            df['jitter'][nDone] = jitter
            if dirOrLocalize:
                print("resp= ",resp)
                df['respX'][nDone] = resp[0]
                df['respY'][nDone] = resp[1]
                df['dx'][nDone] = resp[0] - probePos1[0]
                df['dy'][nDone] = resp[1] - probePos1[1]
                df['afterimageGenesis'][nDone] = afterimageGenesis
                df['afterimageDur'][nDone] = afterimageDur
            else:
                df['respLeftRight'][nDone] = resp
            print( df.loc[nDone-1:nDone] ) #print this trial and previous trial, only because theres no way to print object (single record) in wide format
        #print('trialnum\tsubject\tprobeX\tprobeY\tstartLeft\tupDown\tTilt\tJitter\tDirection\t', file=dataFile)
        #Should be able to print from the dataFrame in csv format
        oneTrialOfData = (str(nDone)+'\t'+participant+'\t'+ "%2.2f\t"%thisTrial['probeX'] + "%2.2f\t"%thisTrial['probeY'] + "%2.2f\t"%probePos1[0] +  "%2.2f\t"%probePos1[1] +
                                        "%r\t"%thisTrial['startLeft'] +"%r\t"%thisTrial['upDown'] +  "%r\t"%thisTrial['tilt'] + "%r\t"%jitter)
        if dirOrLocalize:
            oneTrialOfData +=  ("%.2f\t"%df['respX'][nDone]  + "%.2f\t"%df['respY'][nDone] + "%.2f\t"%df['dx'][nDone] + "%.2f\t"%df['dy'][nDone] +
                                                "%.2f\t"%afterimageGenesis + "%.2f"%afterimageDur)
        else:
            oneTrialOfData += "%r"%resp
        print(oneTrialOfData, file= dataFile)
        if nDone< trials.nTotal-1:
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
    #print('df.dtypes=\n',df.dtypes)
    df = df.convert_objects(convert_numeric=True) #convert dtypes from object to numeric
    #df['dist'] = 
    #analyze cases where tilt==0
    tilt = df.loc[:,'tilt']
    neutralStimIdxs = df.loc[tilt==0]
    neutralStimIdxs = (tilt==0)

    if len(neutralStimIdxs)>1:
      if neutralStimIdxs.any(): #Calculate over/under-correction, which is only interpretable when tilt=0
        df['overCorrected']= np.nan
        if not dirOrLocalize: 
            forCalculatn = df.loc[neutralStimIdxs, ['tilt','startLeft','upDown','respLeftRight']]
            overCorrected = calcOverCorrected( forCalculatn )
            print('overCorrected=\n',overCorrected)
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
    print('Summary of tilt\n',np.around(tiltGrp.mean(),3))