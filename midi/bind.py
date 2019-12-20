import json
import util

config = util.getConfig()


class SingleBind:
    def __init__(self, command, displayId=None, newWorkspace=None):
        self.command = command
        print('display id:', displayId)

        self.displayId = displayId
        self.newWorkspace = newWorkspace
    def run(self, command=None):
        if not command:
            command = self.command        
        if self.displayId != None:
            util.setDisplay(self.displayId) # change to specific display
        else:
            print(f"ERROR: specified ({self.displayId}) display not found")
        util.setWorkspace(self.newWorkspace) # optionally name new workspace
        return util.execCommand(command)
    def open(self):
        return self.run()
    def close(self):
        pass

class DoubleBind(SingleBind):
    def __init__(self, command, releaseCommand, workspace=None, newWorkspace=None):
        SingleBind.__init__(self, command, workspace, newWorkspace)
        self.releaseCommand = releaseCommand
    def open(self):
        self.run()
    def close(self):
        print('running release command')
        self.run(self.releaseCommand)

class ToggleBind(SingleBind):
    def __init__(self, command, workspace=None, newWorkspace=None):
        SingleBind.__init__(self, command, workspace, newWorkspace)
        self.process = None
    def open(self):
        self.process = SingleBind.open(self)
    def close(self):
        if self.process != None:
            print("closing bind")
            # kill the process
            #util.killProcess(self.process)
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
        util.setDisplay(self.displayId) # change to specific display
        util.execCommand("sway kill")

class EnvBind(ReleaseBind):
    def __init__(self, env_var):
        ReleaseBind.__init__(self, f"env {env_var}=true urxvt -fg white", f"env {env_var}=false urxvt -fg white")

class ControllerBind:
    def __init__(self, command):
        self.command = command
    def control(self, value):
        return util.execCommand(self.command % (value,))
