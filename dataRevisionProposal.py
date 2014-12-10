from psychopy import visual, tools
from pandas import DataFrame

import codecs, sys
from psychopy import logging

def saveAsWideText(self,fileName,
                   delim='\t',
                   matrixOnly=False,
                   appendFile=True,
                  ):
        """
        Write a text file with the session, stimulus, and data values from each trial in chronological order.
        Also, return a pandas DataFrame containing same information as the file.
    
        That is, unlike 'saveAsText' and 'saveAsExcel':
         - each row comprises information from only a single trial.
         - no summarising is done (such as collapsing to produce mean and standard deviation values across trials).
    
        This 'wide' format, as expected by R for creating dataframes, and various other analysis programs, means that some
        information must be repeated on every row.
    
        In particular, if the trialHandler's 'extraInfo' exists, then each entry in there occurs in every row.
        In builder, this will include any entries in the 'Experiment info' field of the 'Experiment settings' dialog.
        In Coder, this information can be set using something like::
    
            myTrialHandler.extraInfo = {'SubjID':'Joan Smith', 'DOB':1970 Nov 16, 'Group':'Control'}
    
        :Parameters:
    
            fileName:
                if extension is not specified, '.csv' will be appended if the delimiter is ',', else '.txt' will be appended.
                Can include path info.
    
            delim:
                allows the user to use a delimiter other than the default tab ("," is popular with file extension ".csv")
    
            matrixOnly:
                outputs the data with no header row.
    
            appendFile:
                will add this output to the end of the specified file if it already exists.
    
        """
        if self.thisTrialN<1 and self.thisRepN<1:#if both are <1 we haven't started
            logging.info('TrialHandler.saveAsWideText called but no trials completed. Nothing saved')
            return -1
    
        #create the file or print to stdout
        if appendFile:
            writeFormat = 'a'
        else:
            writeFormat = 'w' #will overwrite a file
        if fileName == 'stdout':
            f = sys.stdout
        elif fileName[-4:] in ['.dlm','.DLM', '.tsv', '.TSV', '.txt', '.TXT', '.csv', '.CSV']:
            f = codecs.open(fileName, writeFormat, encoding="utf-8")
        else:
            if delim==',':
                f = codecs.open(fileName+'.csv', writeFormat, encoding="utf-8")
            else:
                f = codecs.open(fileName+'.txt', writeFormat, encoding="utf-8")
    
        # collect parameter names related to the stimuli:
        if self.trialList[0]:
            header = self.trialList[0].keys()
        else:
            header = []
        # and then add parameter names related to data (e.g. RT)
        header.extend(self.data.dataTypes)
        # get the extra 'wide' parameter names into the header line:
        header.insert(0,"TrialNumber")
        if (self.extraInfo != None):
            for key in self.extraInfo:
                header.insert(0, key)
        df = DataFrame(columns = header)
        
        # loop through each trial, gathering the actual values:
        dataOut = []
        trialCount = 0
        # total number of trials = number of trialtypes * number of repetitions:
    
        repsPerType={}
        for rep in range(self.nReps):
            for trialN in range(len(self.trialList)):
                #find out what trial type was on this trial
                trialTypeIndex = self.sequenceIndices[trialN, rep]
                #determine which repeat it is for this trial
                if trialTypeIndex not in repsPerType.keys():
                    repsPerType[trialTypeIndex]=0
                else:
                    repsPerType[trialTypeIndex]+=1
                repThisType=repsPerType[trialTypeIndex]#what repeat are we on for this trial type?
    
                # create a dictionary representing each trial:
                # this is wide format, so we want fixed information (e.g. subject ID, date, etc) repeated every line if it exists:
                if (self.extraInfo != None):
                    nextEntry = self.extraInfo.copy()
                else:
                    nextEntry = {}
    
                # add a trial number so the original order of the data can always be recovered if sorted during analysis:
                trialCount += 1
    
                # now collect the value from each trial of the variables named in the header:
                for parameterName in header:
                    # the header includes both trial and data variables, so need to check before accessing:
                    if self.trialList[trialTypeIndex] and parameterName in self.trialList[trialTypeIndex]:
                        nextEntry[parameterName] = self.trialList[trialTypeIndex][parameterName]
                    elif parameterName in self.data:
                        nextEntry[parameterName] = self.data[parameterName][trialTypeIndex][repThisType]
                    else: # allow a null value if this parameter wasn't explicitly stored on this trial:
                        if parameterName == "TrialNumber":
                            nextEntry[parameterName] = trialCount
                        else:
                            nextEntry[parameterName] = ''
    
                #store this trial's data
                dataOut.append(nextEntry)
                df = df.append(nextEntry, ignore_index=True)
        
        if not matrixOnly:
        # write the header row:
            nextLine = ''
            for parameterName in header:
                nextLine = nextLine + parameterName + delim
            f.write(nextLine[:-1] + '\n') # remove the final orphaned tab character
    
        # write the data matrix:
        for trial in dataOut:
            nextLine = ''
            for parameterName in header:
                nextLine = nextLine + unicode(trial[parameterName]) + delim
            nextLine = nextLine[:-1] # remove the final orphaned tab character
            f.write(nextLine + '\n')
    
        if f != sys.stdout:
            f.close()
            logging.info('saved wide-format data to %s' %f.name)
        return df
        
if __name__ == "__main__":
   # stuff only to run when not called via 'import'
   #Test my functions
   #grab some data outputted from my program, so I can test some analysis code
    ##The psydat file format is literally just a pickled copy of the TrialHandler object that saved it. You can open it with:
    ##dat = tools.filetools.fromFile(dataFileName)
    dataFileName = "data/Hubert_spatiotopicMotion_03Dec2014_15-49.psydat"
    dat = tools.filetools.fromFile(dataFileName)
    type(dat) #<class 'psychopy.data.DataHandler'>
    #dat.data seems to contain the columns I added
    dat.printAsText()
    
    d= dat.data #<class 'psychopy.data.DataHandler'>
    
    df = saveAsWideText(dat,"data/temp.txt",appendFile=False)
    print "saveAsWideText returned a ", type(df)
    print "which prints as \n", df
    print "Its head is \n", df.head()
    #Columns: [TrialNumber, jitter, probeY, startLeft, tilt, upDown, probeX, ran, order, respLeftRight]
    df.to_csv(path_or_buf='data/fromDataframe.txt', sep='\t')
    
    #Test that I know what I'm doing with the dataframe here
    dTry = DataFrame(columns = {'jitter', 'probeY'})
    dTry = dTry.append( {'jitter':3,'probeY':5}, ignore_index=True)
    dTry = dTry.append( {'jitter':4,'probeY':6}, ignore_index=True)

#            df= df.append( thisTrial, ignore_index=True ) #ignore because I got no index (rowname)
#            df['jitter'][nDone] = jitter

