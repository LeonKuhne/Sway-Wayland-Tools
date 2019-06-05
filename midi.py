import rtmidi
import argparse
import os
import subprocess

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
        ReleaseBind.__init__(self, f"env {env_var}=true urxvt", f"env {env_var}=false urxvt")

#
# CONFIG
#

bindings = {
    # apps
    'A2': ReleaseBind('spotify', 'killall spotify', DISPLAY[2], "music"),
    'G2': ToggleBind('firefox', DISPLAY[0], "internet"),
    'C2': ToggleBind('urxvt', DISPLAY[1], "code"),
    # monitoring tools
    'D2': ToggleBind('htop'),
    'E2': EnvBind('bind_nethogs'),
    'F2': EnvBind('bind_iftop'),
    # switching displays
    'D3': SingleBind('', 'code'),
    'B3': SingleBind('', 'music'),
    'A3': SingleBind('', 'internet')
}
port = 2 # 0..n
readTimeout = 250 # ms

#
# CODE
#

# vars
midiin = rtmidi.RtMidiIn()

# noteExp > the expected note
def eventController(midi):
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
            print("controllers currently unsupported")
            pass
    else:
        print(f"{note} not set")

def listenToPort(port):
    # connect to midi
    print(f"Opening port {port}!")
    midiin.openPort(port)

    # read midi messages
    while True:
        event = midiin.getMessage(250) # some timeout in ms
        if event:
            eventController(event)


# connect 
if __name__ == '__main__':
    # parse args
    parser = argparse.ArgumentParser(description='program midi keyboard bindings')
    parser.add_argument("-p", "--ports", help="show all connected ports", action="store_true")
    args = parser.parse_args()

    ports = range(midiin.getPortCount())

    # handle args
    if args.ports:
        print(f"Here are the connected midi devices ({ports.len()}):")
        for i in ports:
            print(midiin.getPortName(i))
    else:
        listenToPort(port)
