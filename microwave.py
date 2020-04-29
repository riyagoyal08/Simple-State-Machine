"""microwave.py - simulate a simple microwave oven controller state machine

Louis Bertrand <louis.bertrand@durhamcollege.ca>
2019-12-09 -- initial version based on watercooler.py 2019-08-22

This is a demonstration of a simple state machine.
The microwave oven waits for the user to input a number of seconds (integers 0-9) to cook then hit the S button to start.
The state machine has two states: IDLE, COOKING
IDLE -- time_entered / start heating --> COOKING 
COOKING -- time_out / stop the heating --> IDLE

"""

import time
import msvcrt # built-in module to read keyboard in Windows


# System constants
TESTING = True

# Event definitions
EVENT_START = 'S' # User pressed the Start button
EVENT_PAUSE='P'

# Support functions

def log(s):
    """Print the argument if testing/tracing is enabled."""
    if TESTING:
        print(s)

def get_event():
    """Non-blocking keyboard reader. Returns "" if no key pressed."""
    x = msvcrt.kbhit()
    #print(x)
    if x: 
        ret = (msvcrt.getch().decode("utf-8")).upper()
        log("Event " + ret)
    else: 
        ret = ""
    return ret

###
# State machine
###
class MicrowaveMachine(object):
    """Control a virtual microwave oven."""
    def __init__(self):
        self.state = None  # current state
        self.states = {}  # dictionary of states
        self.event = ""  # no event detected
        self.cook_time = 0

    def add_state(self, state):
        self.states[state.name] = state

    def go_to_state(self, state_name):
        if self.state:
            log('Exiting %s' % (self.state.name))
            self.state.exit(self)
        self.state = self.states[state_name]
        log('Entering %s' % (self.state.name))
        self.state.enter(self)

    def update(self):
        if self.state:
            #log('Updating %s' % (self.state.name))
            self.state.update(self)


###
# States
###
class State(object):
    """Abstract parent state class."""
    def __init__(self):
        pass

    @property
    def name(self):
        return ''

    def enter(self, machine):
        pass

    def exit(self, machine):
        pass

    def update(self, machine):
        pass


class IdleState(State):
    """Waiting for time and start."""
    def __init__(self):
        State.__init__(self)

    @property
    def name(self):
        return "IDLE"

    def enter(self, machine):
        machine.cook_time=0
        

    def exit(self, machine):
        State.exit(self, machine)

    def update(self, machine):
        State.update(self, machine)
        if machine.event == EVENT_START:
            machine.go_to_state("COOKING")
        elif machine.event and machine.event in "0123456789":
            machine.cook_time = (machine.cook_time * 10) + int(machine.event)
            print(machine.cook_time)

class PauseState(State):
    def __init__(self):
        State.__init__(self)
    
    @property
    def name(self):
        return 'Pause'

    def enter(self,machine):
        print("Paused")
    
    def update(self,machine):
        if machine.event==EVENT_START:
            machine.go_to_state('COOKING')
        elif machine.event=='Q':
            machine.go_to_state('IDLE')

    def exit(self,machine):
        State.exit(self,machine)
        
class CookingState(State):
    """The heater is on."""

    def __init__(self):
        State.__init__(self)

    @property
    def name(self):
        return "COOKING"

    def enter(self, machine):
        print("Start heating")
        # For testing, divide the cook time by 10 (we are impatient!)
        machine.stop_time = time.monotonic() + machine.cook_time 

    def exit(self, machine):
        print("Stop heating")
        

    def update(self, machine):
        if machine.stop_time <= time.monotonic():
            machine.go_to_state("IDLE")
        elif machine.event == "Q":
            print("Cancel")
            machine.go_to_state("IDLE")
        elif machine.event==EVENT_PAUSE:
            machine.cook_time=machine.stop_time-time.monotonic()
            machine.go_to_state("Pause")
        else:
            print(".", end="", flush=True)
            time.sleep(0.2)


###
# Main program starts here
###
if __name__ == "__main__":
    # new machine object
    microwave = MicrowaveMachine()

    # Add the states
    microwave.add_state(IdleState())  
    microwave.add_state(CookingState())
    microwave.add_state(PauseState())


    # Reset state is "waiting for water bottle"
    microwave.go_to_state("IDLE")

    # begin continuous processing of events
    while True:
        try:
            microwave.event = get_event()
            microwave.update()
        except KeyboardInterrupt:
            print("shutdown")
            break

