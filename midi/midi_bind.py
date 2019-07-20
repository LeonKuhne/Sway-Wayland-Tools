import json
import midi_util as util

config = util.getConfig()

# 
# Binding Classes
#

class SingleBind:
    def __init__(self, command, workspace=None, newWorkspace=None):
        self.command = command
        self.isDisplay = workspace in config['displays'] # determine if workspace is a display
        self.workspace = workspace
        self.newWorkspace = newWorkspace
    def open(self):
        if self.isDisplay:
            displayID = config['displays'].index(self.workspace)
            util.setDisplay(displayID) # change to specific display
        else:
            util.setWorkspace(self.workspace) # change to specific workspace
        
        util.setWorkspace(self.newWorkspace) # optionally name new workspace
        return util.execCommand(self.command)
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
        util.execCommand(self.releaseCommand)

class KillOnReleaseBind(SingleBind):
    def close(self):
        displayID = config['displays'].index(self.workspace)
        util.setDisplay(displayID) # change to specific display
        util.execCommand("sway kill")


class EnvBind(ReleaseBind):
    def __init__(self, env_var):
        ReleaseBind.__init__(self, f"env {env_var}=true urxvt -fg white", f"env {env_var}=false urxvt -fg white")

class ControllerBind:
    def __init__(self, command):
        self.command = command
    def control(self, value):
        return util.execCommand(self.command % (value,))
