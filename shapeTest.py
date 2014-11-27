from psychopy import visual, event, core, info
#For discussion of errors see
# https://groups.google.com/forum/#!topic/psychopy-users/0XfpU2Uko_c
myWin = visual.Window([600,600], monitor='testMonitor', units='deg')

#try:
#    runInfo = info.RunTimeInfo(
#            # if you specify author and version here, it overrides the automatic detection of __author__ and __version__ in your script
#            #author='<your name goes here, plus whatever you like, e.g., your lab or contact info>',
#            #version="<your experiment version info>",
#            win=myWin,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
#            refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
#            verbose=True, ## True means report on everything 
#            userProcsDetailed=True  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
#                                    #seems to require internet access, probably for process lookup
#            )
#print(runInfo)
#    print runInfo
#except:
#    print('Runinfo failed')

blackDot = visual.Circle(myWin,units='deg',radius=3)
blackDot.fillColor='black' #works
blackDot.setFillColor('black') #works
blackDot.setFillColor((-1,-1,-1),'rgb') #works
blackDot.color='black'  #TypeError: 'NoneType' object is not callable

location=(0,0)
#blackDot.setColor('black') #TypeError: 'NoneType' object is not callable
notClicked = True
while notClicked: #collecting response
    blackDot.setPos(location)
    blackDot.draw()
    myWin.flip()
    #handle key presses each frame
    for key in event.getKeys():
        if key in ['escape','q']:
            notClicked = False
            
myWin.close()
core.quit()
                    
#STOP

