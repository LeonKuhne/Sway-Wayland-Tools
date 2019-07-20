import os
import subprocess
import json


def getConfig():
    with open('midi.json', 'r') as config_file:
        return json.loads(config_file.read())

def setWorkspace(workspaceName):
    if(workspaceName != None):
        os.system(f'sway workspace {workspaceName}')

def setDisplay(displayId):
    os.system(f"sway focus output {config['displays'][displayId]}")

def execCommand(command):
    print(f"executing '{command}'")
    return subprocess.Popen(command, shell=True)


