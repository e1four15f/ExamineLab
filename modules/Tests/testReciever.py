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
    
    for path, _, files in os.walk(path2load):
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
    :launch_command: -- command to perform execution
    '''


    def __init__(self, launch_command = './'):
        '''
        Loads *pathMapping* with config file interpreted as dict and initializes launch_command.
        '''

        self.launch_command = launch_command

    def get_test_by_path(self, path, preproc = None):
        '''
        Returns one test 
        '''
        return load_file(path, preproc)
    
    def get_tests_by_paths(self, paths, preproc = None):
        for path in paths:
            yield self.get_test_by_path(path, preproc)

    def spawn_user_proc(self, uinput)-> tuple:

        proc = subprocess.run(self.launch_command, input = uinput, stdout = subprocess.PIPE, stderr = subprocess.PIPE, encoding='utf-8', shell = True)
        #print(f'in spawn_user_proc -- {proc.stdout} -- {proc.args}')
        
        return (proc.stdout, proc.stderr)


    def perform_testing(self, tests, test_preproc = None, input_preproc = None):
        
        output = [re.sub(r'\r', '', test.output) + '\n' for test in tests]
        inputs = [re.sub(r'\r', '', test.input) for test in tests]
      
        program_outs = [self.spawn_user_proc(pr_input)
                            for pr_input in inputs]
            
        
        passed = {}
        print(f'program inputs: {inputs}')
        print(f'program outs  : {program_outs}')

        print(f'tests         : {output}')
        for i, b in verification.verifyMultiple([stdout[0] for stdout in program_outs], output):
            passed[tests[i].pk] = b
            print('tests: ', tests[i].title, i, passed[tests[i].pk])
            
        return (passed, program_outs)


def perform_testing_from_text(user_pr_text, tests, language, test_preproc = None, input_preproc = None):

    lang, launch_command, optargs = language.extention, None, None

    if os.name == 'posix':
        launch_command = language.launch_command_linux
        optargs = language.optional_linux
    else:
        launch_command = language.launch_command_win
        optargs = language.optional_win

    user_hash = 'program' + str(hash(user_pr_text))
    user_code_pth = user_hash + lang

    with open(user_code_pth,'w') as user_pr:
        user_pr.write(user_pr_text)
    
    abspath = os.path.abspath(user_code_pth)
    abspath_wo_ext = abspath.split('.')[0]

    launch_command = re.sub(r'<path>', abspath_wo_ext, launch_command)
    optargs = re.sub(r'<path>', abspath_wo_ext, optargs)

    test_checker = TestReciever(launch_command)
    tests_result, outs = test_checker.perform_testing(tests, test_preproc, input_preproc)

    #
    subprocess.run(optargs, shell = True)
    return (tests_result, outs)
