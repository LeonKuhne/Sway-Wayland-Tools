import rtmidi
import argparse
import os
import subprocess
import json

DISPLAY = ['DP-1', 'DVI-D-1', 'HDMI-A-1', 'DVI-D-2']

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

class KillOnReleaseBind(SingleBind):
    def close(self):
        displayID = DISPLAY.index(self.workspace)
        setDisplay(displayID) # change to specific display
        execCommand("sway kill")


class EnvBind(ReleaseBind):
    def __init__(self, env_var):
        ReleaseBind.__init__(self, f"env {env_var}=true urxvt -fg white", f"env {env_var}=false urxvt -fg white")

class ControllerBind:
    def __init__(self, command):
        self.command = command
    def control(self, value):
        return execCommand(self.command % (value,))

#
# CONFIG
#

with open('midi.json', 'r') as midi_file:
    config = json.loads(midi_file.read())

toolsDir = '~/.tools'

#
# CODE
#

# vars
midi_in = rtmidi.RtMidiIn()

# noteExp > the expected note
def eventController(midi, bindings):
    midi.getNoteNumber()
    note = midi.getMidiNoteName(midi.getNoteNumber())
    velocity = midi.getVelocity()
    
    # controller logic
    if note in bindings:
        print(bindings[note])
        binding = eval(bindings[note])
        print(binding)

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
    midi_in.openPort(port+1)

    # read midi messages
    while True:
        event = midi_in.getMessage(config['timeout']) # some timeout in ms
        if event:
            bindings = config['bindings'][port]
            print(bindings)

            # TODO convert string bindings to objects
            bindings = bindings


            callback(event, bindings)


# connect 
if __name__ == '__main__':
    # parse args
    parser = argparse.ArgumentParser(description='program midi keyboard bindings')
    parser.add_argument("-i", "--info", help="show all connected ports", action="store_true")
    parser.add_argument("-l", "--listen", help="listen to input", action="store_true")
    parser.add_argument("-p", "--port", help="specify midi port to use")
    args = parser.parse_args()

    # get port
    port = config['default_port']
    if args.port:
        temp_port = int(args.port)
        if temp_port < midi_in.getPortCount():
            port = temp_port
            print(f"Using specified port {port}")
        else:
            print(f"Couldn't find specified port {args.port}, using (default) {port} instead")

    # handle args
    if args.info:
        print(f"Here are the connected midi devices ({len(ports)}):")
        for port_num in range(midi_in.getPortCount()): 
            print(port_num)
    elif args.listen:
        listenToPort(port, print) 
    else:
        listenToPort(port, eventController) 
