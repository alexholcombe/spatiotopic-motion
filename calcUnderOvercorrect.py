from pandas import DataFrame

#calculate whether under- or over-correcting
def underOverCorrected(df):
    #Expect dataframes with fields tilt, startLeft, upDown, respFwdBackslash
    #Actually only can give legitimate answer when tilt is 0, because only that is an ambiguous stimulus
    #canonical case is startLeft, upDown, tilt 0
    #    1
    #A     B
    #    2
    #If you undercorrect, /  fwdSlash
    #startLeft mean target moves to right? So upDown undercorrect would be fwdslash
    startLeft = df.loc['startLeft']
    upDown = df.loc['upDown']
    if respFwdBackslash: #for canonical case. backslash means overcorrect
        underCorrect = False
    else:
        underCorrect = True #fwdslash means undercorrect
    #any departure from canonical case inverts the answer
    if not startLeft: #otherwise-canonical case gives backslash
        underCorrect = not underCorrect
    if not upDown:
        underCorrect = not underCorrect
    
    respFwdBackslash= df.loc['respFwdBackslash']
    underCorrect = underCorrect 
    #print('startLeft*2=',startLeft*2)
    #ans= startLeft*2-1 * upDown*2-1 * respFwdBackslash
    return ans

DataFrame
data = {'tilt': [0,0]
df = DataFrame({'tilt': , index=[nDone],
                            columns = ['jitter','probeX','probeY','startLeft','tilt','upDown']) #columns included purely to specify their order
forCalculatn = df.loc[neutralStimIdxs, ['tilt','startLeft','upDown','respFwdBackslash']]
