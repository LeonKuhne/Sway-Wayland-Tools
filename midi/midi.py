import rtmidi
import argparse
import bind
import util


# vars
config = util.getConfig()
midi_in = rtmidi.RtMidiIn()


def eventController(midi, bindings):
    midi.getNoteNumber()
    note = midi.getMidiNoteName(midi.getNoteNumber())
    velocity = midi.getVelocity()
    
    # controller logic
    if note in bindings:
        binding = eval(f'bind.{bindings[note]}')

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
            callback(event, bindings)


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
