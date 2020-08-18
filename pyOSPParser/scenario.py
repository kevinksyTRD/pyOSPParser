""" Contains classes for creating, importing and deploying
a scenario for co-simulation from Open Simulation Platform

Classes:
    OSPEvent: Class for event in OSP scenario
    OSPScenario: Class for scenario in OSP scenario that contains
    collection of OSPEvent instances
    EventAction: Enumerator for type of actions used in OSPEvent

Functions:
    format_filename(str): Converts any string to a valid file name

"""

import json
import string
from enum import Enum


def format_filename(name: str) -> str:
    """Take a string and return a valid filename constructed from the string.
Uses a whitelist approach: any characters not present in valid_chars are
removed. Also spaces are replaced with underscores.

Note: this method may produce invalid filenames such as ``, `.` or `..`
When I use this method I prepend a date string like '2009_01_15_19_46_32_'
and append a file extension like '.txt', so I avoid the potential of using
an invalid filename.
"""
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in name if c in valid_chars)
    filename = filename.replace(' ', '_')
    return filename


class EventAction(Enum):
    override = 1
    bias = 2
    reset = 3


class OSPEvent:
    """Class for event in OSP scenario

    Attributes
    ----------
        OVERRIDE(int): value for override action
        BIAS(int): value for bias action
        RESET(int): value for reset action
    """

    OVERRIDE = 1
    BIAS = 2
    RESET = 3

    def __init__(
            self,
            time: float,
            model: str,
            variable: str,
            action: int,
            value: float
    ):
        """Constructor for OSPEvent

        Args:
            time(float): Time for the event
            model(str): model name
            variable(str): variable name
            action(int): Action type. 1 for override, 2 for bias and 3 for reset.
                Consider using the attributes of the class: OVERRIDE, BIAS and RESET
            value(float): Value for the action
        """
        self.time = time
        self.model = model
        self.variable = variable
        self.action = action
        self.value = value

    def to_dict(self):
        return {
            'time': self.time, 'model': self.model,
            'variable': self.variable, 'action': EventAction(self.action).name,
            'value': int(self.value) if int(self.value) == self.value else self.value
        }


class OSPScenario:
    events = []

    def __init__(self, name: str, end: float, description: str = ''):
        """Initialization of OSPScenario object

        Args:
            name(str): Name of the scenario
            end(float): End time in second
            description(str): Description of the scenario
        """
        self.name = name
        self.end = end
        self.description = description

    def add_event(self, event: OSPEvent):
        if type(event) is not OSPEvent:
            raise TypeError("The event should be an instance of OSPEvent class")
        self.events.append(event)

    def to_dict(self):
        return {
            'description': self.description,
            'events': [event.to_dict() for event in self.events],
            'end': self.end,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)

    def from_json(self, json_str):
        scenario_dict = json.loads(json_str)
        self.description = scenario_dict['description']
        self.end = scenario_dict['end']
        self.events = []
        for event in scenario_dict['events']:
            model = event['model']
            variable = event['variable']
            self.events.append(OSPEvent(
                time=event['time'],
                model=model,
                variable=variable,
                action=EventAction.__getitem__(event['action']).value,
                value=event['value']
            ))

    def get_file_name(self):
        return '%s.json' % format_filename(self.name)
