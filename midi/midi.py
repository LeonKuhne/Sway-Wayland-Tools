import rtmidi
import argparse
import bind
import util
import time

# vars
midi_in = rtmidi.MidiIn()
midi_out = rtmidi.MidiOut()


def eventController(midi, bindings):
    noteInfo = midi[0]
    controlType = noteInfo[0]
    note = str(noteInfo[1])
    noteValue = noteInfo[2]
    print(noteInfo)

    # controller logic
    if note in bindings:
        binding = eval(f'bind.{bindings[note]}')
        print("value:", binding)

        if controlType == 153:  # pad open
            binding.open()
        elif controlType == 137:  # pad release
            binding.close()
        elif controlType == 176:  # controller
            binding.control(noteValue/127)
        else:  # button TODO: handle keys
            if noteValue == 64 or noteValue == 137:  # off
                print("closing binding")
                binding.close()
            else:  # on
                print("opening binding")
                binding.open()

    else:
        print(f"{note} not set")


def listenToPort(port, callback):
    config = util.getConfig()

    # connect to midi
    print(f"Opening port {port}!")
    midi_in.open_port(port+1)

    # read midi messages
    while True:
        event = midi_in.get_message()
        time.sleep(config['timeout']/1000.0)
        if event:
            print(event)
            config = util.getConfig()  # live config updating
            bindings = config['bindings'][port]
            callback(event, bindings)


if __name__ == '__main__':
    config = util.getConfig()

    # parse args
    parser = argparse.ArgumentParser(
        description='program midi keyboard bindings')
    parser.add_argument(
        "-i", "--info", help="show all connected ports", action="store_true")
    parser.add_argument(
        "-l", "--listen", help="listen to input", action="store_true")
    parser.add_argument("-p", "--port", help="specify midi port to use")
    parser.add_argument("-b", "--blink", help="blink a specific light")
    args = parser.parse_args()

    # get port
    port = config['default_port']
    if args.port:
        temp_port = int(args.port)
        if temp_port < len(midi_in.get_ports()):
            port = temp_port
            print(f"Using specified port {port}")
        else:
            print(
                f"Couldn't find specified port {args.port}, using (default) {port} instead")

    # handle args
    if args.info:
        ports = midi_in.get_ports()
        print(f"Here are the connected midi devices ({len(ports)}):")
        for port_num in range(0, len(ports)):
            print(f"{port_num}: {ports[port_num]}")

    elif args.blink:
        midi_out.open_port(port)

        note = int(args.blink)
        print(f"blinking {note}")

        # TODO get this working
        for i in range(3):
            # on
            midi_out.send_message([144, note, 90])
            time.sleep(0.5)

            # off
            midi_out.send_message([128, note, 40])
            time.sleep(0.5)

    elif args.listen:
        listenToPort(port, print)
    else:
        listenToPort(port, eventController)
