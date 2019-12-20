import os
import subprocess
import json


def getConfig():
    with open('/home/x/.config/midi/config.json', 'r') as config_file:
        return json.loads(config_file.read())


def setWorkspace(workspaceName):
    if(workspaceName != None):
        os.system(f'sway workspace {workspaceName}')

def setDisplay(displayId):
    print("display:", displayId)
    config = getConfig()
    display = config['displays'][displayId]
    print(display)
    os.system(f"sway focus output {display}")

def execCommand(command):
    print(f"executing '{command}'")
    return subprocess.Popen(command, shell=True, preexec_fn=os.setsid)

def killProcess(process):
    os.killpg(os.getpgid(pro.pid), signal.SIGTERM)

