import os
import re
import subprocess
import testVerification as verification

def loadFromDir(path2load, preproc = None):
        '''
        Returns generator to loaded files.
        Accepts *preproc* -- preprocessing function, that can be passed to preprocess contents of read file
        '''
        if not callable(preproc):
            raise AttributeError('*preproc* must be a function')
        for path, directory, files in os.walk(path2load):
            for filename in files:
                with open(path + '/' +filename, 'r') as testFile:
                    if preproc == None:
                        yield testFile.read()
                    else:
                        yield preproc(testFile.read())

class TestReciever:

    '''
    *rawConfig* -- Raw contents of config file
    *pathMapping* -- Dictionary to map requested URI to 
    *launchCommand* -- command to perform execution
    '''
    rawConfig = str()
    pathMapping = {}
    launchCommand = str()

    def __init__(self, configPath, launchCommand = './'):
        with open(configPath, 'r') as configFile:
            self.rawConfig = configFile.read()
        #TODO Do we need security here?
        pathMapping = eval(self.rawConfig)
        self.launchCommand = launchCommand
    
    def getTestByUri(self, uri, preproc = None):
        path = self.pathMapping[uri]
        return loadFromDir(path, preproc)
    
    def getTestsByUris(self, URIs, preproc = None):
        for uri in URIs:
            yield self.getTestByUri(uri, preproc)

    def spawnUserProc(self, userProgramPath, input, args = None):
        if not issubclass(args, list):
            raise TypeError('*args* must be a list of commandline arguments')

        if args != None:
            return subprocess.check_output([self.launchCommand] + args + [userProgramPath,  input])

    def performTesting(self, userProgramPath, inputDir, URIs, testPreproc = None, inputPreproc = None, args = None):
        
        tests = [self.getTestsByUris(URIs, preproc = testPreproc)]
        inputs = [loadFromDir(inputDir, preproc = inputPreproc)]
        programOuts = [self.spawnUserProc(userProgramPath,
                                          prInput,
                                          args)
                                          for prInput in inputs]
                                          
        return list(verification.verifyMultiple(programOuts, tests))
                