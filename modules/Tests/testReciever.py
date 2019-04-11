import os
import threading
import re
import subprocess
import signal
from modules.Tests import testVerification as verification

def load_from(path2load, preproc = None, dir = True):
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

def load_file(path2load, preproc = None):
    return list(load_from(path2load, preproc, dir = False))[0]

class TestReciever:

    '''
    :launchCommand: -- command to perform execution
    '''


    def __init__(self, launchCommand = './'):
        '''
        Loads *pathMapping* with config file interpreted as dict and initializes launchCommand.
        '''

        self.launchCommand = launchCommand

    def get_test_by_path(self, path, preproc = None):
        '''
        Returns one test 
        '''
        path = self.pathMapping[uri]
        return load_file(path, preproc)
    
    def get_tests_by_paths(self, paths, preproc = None):
        for path in paths:
            yield self.get_test_by_path(path, preproc)

    def spawn_user_proc(self, user_pr_path, uinput, args = None):
        if args != None and not issubclass(type(args), list):
            raise TypeError(f':args: must be a list of commandline arguments, not {type(args)}')

        subproc_args = None
        if args == None:
            subproc_args = [self.launchCommand] + [os.path.abspath(user_pr_path)]
        else:
            subproc_args = [self.launchCommand] + args + [os.path.abspath(user_pr_path)]
            
        #proc = subprocess.Popen(subproc_args, stdout=subprocess.PIPE)
        #threading.Timer(5, proc.terminate())
        proc = subprocess.run(subproc_args, input = uinput, capture_output=True, encoding='utf-8')
        print(f'in spawn_user_proc -- {proc.stdout} -- {proc.args}')
        print(subproc_args)
        
        return proc.stdout


    def perform_testing(self, user_pr_path, input_dir, test_paths, test_preproc = None, input_preproc = None, args = None):
        
        print('in perform_testing')
        tests = [self.get_tests_by_paths(test_paths, preproc = test_preproc)]
        inputs = list(load_from(input_dir, preproc = input_preproc))
        program_outs = []
        for pr_input in inputs:
            program_outs.append(self.spawn_user_proc(user_pr_path, pr_input, args))
        passed = {}

        print(program_outs)
        for i, b in verification.verifyMultiple(program_outs, tests):
            passed[test_paths[i]] = b
            
        return passed
