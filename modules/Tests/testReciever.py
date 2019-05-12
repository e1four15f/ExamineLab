import os
import threading
import re
import subprocess
import signal

from modules.Tests import testVerification as verification
from threading import Thread, Event

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

    def spawn_user_proc(self, uinput, timeout)-> tuple:
        proc = None 
        def out_of_time(signum, frame):
            raise RuntimeError('Out of time')

        signal.signal(signal.SIGALRM, out_of_time)
        signal.alarm(timeout)
        proc = subprocess.run(self.launch_command,
                              timeout,
                              input = uinput,
                              stdout = subprocess.PIPE, 
                              stderr = subprocess.PIPE, 
                              encoding='utf-8', 
                              shell = True)

        signal.signal(signal.SIG_IGN, lambda s,f: s)
        signal.alarm(0)

        print(f'in spawn_user_proc -- {proc.stdout} -- {proc.args}')
        
        return (proc.stdout, proc.stderr)


    def perform_testing(self, tests, timeout,  test_preproc = None, input_preproc = None, user_preproc = lambda out: out):
        
        output = None
        inputs = None
        program_outs = None 

        if test_preproc is None:
            output = [re.sub(r'\r', '', test['output']) for test in tests]
        else:
            output = [re.sub(r'\r', '', test_preproc(test['output'])) for test in tests]
        
        if input_preproc is None:
            inputs = [re.sub(r'\r', '', test['input']) for test in tests]
        else:
            inputs = [re.sub(r'\r', '', input_preproc(test['input'])) for test in tests]

        passed = {}

        try:
            program_outs = [self.spawn_user_proc(pr_input, timeout)
                            for pr_input in inputs]
        except RuntimeError:
            for i in range(len(output)):
                passed[tests[i]['id']] = False 
            return (passed, [('', f'Время выполнения программы превысило {timeout} сек.')]*len(output))

        
        print(f'program inputs: {inputs}')
        print(f'program outs  : {program_outs}')
        print(f'tests         : {output}')

        for i, b in verification.verifyMultiple([user_preproc(stdout[0]) for stdout in program_outs], output):
            passed[tests[i]['id']] = b
            print('tests: ', tests[i]['title'], i, passed[tests[i]['id']])
            
        return (passed, program_outs)


def perform_testing_from_text(user_pr_text, tests, language, test_preproc = None, input_preproc = None, user_preproc = None, timeout = 2):
    lang = language['extention']
    launch_command = language['launch_command_linux']
    optargs = language['optional_linux']

    user_hash = 'program' + str(hash(user_pr_text))
    user_code_pth = user_hash + lang

    with open(user_code_pth,'w') as user_pr:
        user_pr.write(user_pr_text)
    
    abspath = os.path.abspath(user_code_pth)
    abspath_wo_ext = abspath.split('.')[0]

    launch_command = re.sub(r'<path>', abspath_wo_ext, launch_command)
    optargs = re.sub(r'<path>', abspath_wo_ext, optargs)

    test_checker = TestReciever(launch_command)
    tests_result, outs = test_checker.perform_testing(tests, timeout, test_preproc, input_preproc, user_preproc)

    subprocess.run(optargs, shell = True)
    return (tests_result, outs)
