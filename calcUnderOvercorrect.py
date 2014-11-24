from __future__ import print_function
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
    startLeft = df['startLeft']
    upDown = df['upDown']
    respFwdBackslash= df['respFwdBackslash']
    underCorrect = ~ respFwdBackslash #tilde is bitwise NOT have to use it to apply operation to each element
    #for canonical case. backslash means overcorrect, fwdslash means undercorrect
    #any departure from canonical case inverts the answer. Use XOR (^) to invert conditional on another boolean.
    startLeft_not_canonical = ~ startLeft #startLeft = True is canonical case. So, flip otherwise
    underCorrect = underCorrect ^ startLeft_not_canonical
    upDown_not_canonical = ~ upDown #otherwise-canonical case gives backslash
    underCorrect =  underCorrect ^ upDown_not_canonical
    return underCorrect

data = {'tilt': [0,0,-2,-2], 'startLeft':[True, True,True,True], 'upDown':[True, True,True,False], 'respFwdBackslash':[False,True,True,True]}
df = DataFrame(data , #index=[nDone],
                            columns = ['tilt','startLeft','upDown','respFwdBackslash']) #columns included purely to specify their order
#forCalculatn = df.loc[neutralStimIdxs, ['tilt','startLeft','upDown','respFwdBackslash']]
underCorrected = underOverCorrected(df.loc[0])
print('underCorrected=',underCorrected)
underCorrected = underOverCorrected(df)
print('underCorrected=\n',underCorrected)

#forCalculatn = df.loc[neutralStimIdxs, ['tilt','startLeft','upDown','respFwdBackslash']]
