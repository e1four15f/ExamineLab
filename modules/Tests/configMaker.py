import os
import datetime
import re 
def makeConfig(filesDir, language, task, filetype = None):
    '''
    :filesDir: -- directory with files
    :task: -- Name or number of the task
    :filetype: -- filetypes to include in config
    '''
    configDict = {}
    
    for path, dirs, filenames in os.walk(filesDir):
        for filename in filenames:
            if filetype != None:
                if not re.search('\\.{type}$'.format(type = filetype),filename):
                    continue
            key = str(hash(path)) + str(hash(filename))
            configDict[key] = os.path.abspath(path + '/' + filename)
    with open(language + str(task) + str(datetime.datetime.now()), 'w') as config:
        config.write(repr(configDict))
        config.close()
           

