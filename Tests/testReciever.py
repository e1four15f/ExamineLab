import os
import re
import subprocess
import testVerification as verification

def loadFrom(path2load, preproc = None, dir = True):
    '''
    Returns generator to loaded files if *dir* is True. Else -- only file from path
    Accepts *preproc* -- preprocessing function, that can be passed to preprocess contents of read file
    '''
    if preproc != None and not callable(preproc):
        raise AttributeError('*preproc* must be a function')
    
    if not dir:
        with open(path2load, 'r') as file:
            if preproc != None:
                yield preproc(file.read())
            else:
                yield file.read()
            return
    
    for path, directory, files in os.walk(path2load):
        for filename in files:
            with open(path + '/' +filename, 'r') as testFile:
                if preproc == None:
                    yield testFile.read()
                else:
                    yield preproc(testFile.read())
        return

def loadFile(path2load, preproc = None):
    return list(loadFrom(path2load, preproc, dir = False))[0]

class TestReciever:

    '''
    *configPath* -- path to load config file
    *rawConfig* -- Raw contents of config file
    *pathMapping* -- Dictionary to map requested URI to 
    *launchCommand* -- command to perform execution
    '''

    configPath = str()
    rawConfig = str()
    pathMapping = {}
    launchCommand = str()

    def __init__(self, configPath, launchCommand = './'):
        '''
        Loads *pathMapping* with config file interpreted as dict and initializes launchCommand.
        '''
        self.configPath = configPath

        with open(configPath, 'r') as configFile:
            self.rawConfig = configFile.read()
        
        #TODO Do we need security here?
        self.pathMapping = eval(self.rawConfig)
        self.launchCommand = launchCommand

    def save(self):
        self.rawConfig = repr(self.pathMapping)
        with open(self.configPath, 'w') as config:
            config.write(self.rawConfig)

    
    def getTestByUri(self, uri, preproc = None):
        '''
        Returns one test 
        '''
        path = self.pathMapping[uri]
        return loadFile(path, preproc)
    
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
        inputs = [loadFrom(inputDir, preproc = inputPreproc)]
        programOuts = [self.spawnUserProc(userProgramPath,
                                          prInput,
                                          args)
                                          for prInput in inputs]

        return verification.verifyMultiple(programOuts, tests)

