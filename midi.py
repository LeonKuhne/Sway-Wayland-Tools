import rtmidi
import argparse
import os
import subprocess
import time
from threading import Thread

DISPLAY = ['DVI-D-1', 'DVI-D-2', 'HDMI-A-1']

#
# Helper Functions
#

def setWorkspace(workspaceName):
    if(workspaceName != None):
        os.system(f'sway workspace {workspaceName}')

def setDisplay(displayId):
        os.system(f'sway focus output {DISPLAY[displayId]}')

def execCommand(command):
    print(f"executing '{command}'")
    return subprocess.Popen(command, shell=True)

# 
# BINDING TYPES
#

class SingleBind:
    def __init__(self, command, workspace=None, newWorkspace=None):
        self.command = command
        self.isDisplay = workspace in DISPLAY # determine if workspace is a display
        self.workspace = workspace
        self.newWorkspace = newWorkspace
    def open(self):
        if self.isDisplay:
            displayID = DISPLAY.index(self.workspace)
            setDisplay(displayID) # change to specific display
        else:
            setWorkspace(self.workspace) # change to specific workspace
        
        setWorkspace(self.newWorkspace) # optionally name new workspace
        return execCommand(self.command)
    def close(self):
        pass

class ToggleBind(SingleBind):
    def __init__(self, command, workspace=None, newWorkspace=None):
        SingleBind.__init__(self, command, workspace, newWorkspace)
        self.process = None
    def open(self):
        self.process = SingleBind.open(self)
    def close(self):
        if self.process != None:
            print("closing bind")
            self.process.terminate()
            self.process = None
        else:
            print("already closed")

class ReleaseBind(SingleBind):
    def __init__(self, command, releaseCommand, workspace=None, newWorkspace=None):
        SingleBind.__init__(self, command, workspace, newWorkspace)
        self.releaseCommand = releaseCommand
    def close(self):
        execCommand(self.releaseCommand)

class EnvBind(ReleaseBind):
    def __init__(self, env_var):
        ReleaseBind.__init__(self, f"env {env_var}=true urxvt -fg white", f"env {env_var}=false urxvt -fg white")

class ControllerBind:
    def __init__(self, command, delay=0):
        self.command = command
        self.lastRun = 0
        self.queueCmd = None
        self.delay = delay/1000
    def control(self, value):
        cmd = self.command % (value,)
        now = time.time()
        timeDelta = now - self.lastRun
        if timeDelta > self.delay:
            # execute command immediately
            self.lastRun = now
            execCommand(cmd)
            self.queueCmd = None
        else:
            # execute command after delay
            if self.queueCmd == None:
                # run last command at the next update time
                self.queueCmd = cmd
                delayWait = self.delay-timeDelta
                runAfterDelay = Thread(target=self.runAfterDelay, args=(delayWait,))
                runAfterDelay.start()
            else:
                self.queueCmd = cmd
    def runAfterDelay(self, delay):
        # run after delay
        self.lastRun = time.time()
        time.sleep(delay)
        execCommand(self.queueCmd)
        self.queueCmd = None

#
# CONFIG
#

port = 2 # default port 0..n
readTimeout = 250 # ms
toolsDir = '~/.tools'

BINDING = [
    {},
    { # NANO
        'A#-2': ToggleBind('playerctl play'),
        'B-2': ToggleBind('playerctl pause'),
        'D-1': ToggleBind('playerctl next'),
        'C#-1': ToggleBind('playerctl previous'),
        'C1': ControllerBind(f'{toolsDir}/set_volume.sh %s'),
        'C#1': ControllerBind(f'redshift -l 43.79924:-72.1228 -g %s -r -o', 2000)
    },
    { # AKAI
        # apps
        'A2': ReleaseBind('spotify', 'killall spotify', DISPLAY[2], "music"),
        'G2': ToggleBind('firefox', DISPLAY[0], "internet"),
        'C2': ToggleBind('urxvt -fg white -bg black', DISPLAY[1], "code"),
        # monitoring tools
        'D2': ToggleBind('htop'),
        'E2': EnvBind('bind_nethogs'),
        'F2': EnvBind('bind_iftop'),
        # switching displays
        'D3': SingleBind('', 'code'),
        'B3': SingleBind('', 'music'),
        'A3': SingleBind('', 'internet')
    },
]

#
# CODE
#

# vars
midiin = rtmidi.RtMidiIn()

# noteExp > the expected note
def eventController(midi, bindings):
    midi.getNoteNumber()
    note = midi.getMidiNoteName(midi.getNoteNumber())
    velocity = midi.getVelocity()
    
    # controller logic
    if note in bindings:
        binding = bindings[note]

        if midi.isNoteOn():
            print("opening binding")
            binding.open()
        
        elif midi.isNoteOff():
            print("closing binding")
            binding.close()

        elif midi.isController():
            #print('CONTROLLER', midi.getControllerNumber(), midi.getControllerValue())
            binding.control(midi.getControllerValue()/127)
            pass
    else:
        print(f"{note} not set")

def listenToPort(port, callback):
    # connect to midi
    print(f"Opening port {port}!")
    midiin.openPort(port)

    # read midi messages
    while True:
        event = midiin.getMessage(250) # some timeout in ms
        if event:
            bindings = BINDING[port]
            callback(event, bindings)


# connect 
if __name__ == '__main__':
    # parse args
    parser = argparse.ArgumentParser(description='program midi keyboard bindings')
    parser.add_argument("-i", "--info", help="show all connected ports", action="store_true")
    parser.add_argument("-l", "--listen", help="listen to input", action="store_true")
    parser.add_argument("-p", "--port", help="specify midi port to use")
    args = parser.parse_args()

    ports = range(midiin.getPortCount())
    
    if args.port:
        tempPort = int(args.port)
        if tempPort < midiin.getPortCount() and tempPort > 0:
            print(f"Using specified port {port}")
            port = tempPort
        else:
            print(f"Couldn't find specified port {args.port}, using {port} instead")

    # handle args
    if args.info:
        print(f"Here are the connected midi devices ({len(ports)}):")
        for i in ports:
            print(midiin.getPortName(i))
    elif args.listen:
        listenToPort(port, print) 
    else:
        listenToPort(port, eventController) 
