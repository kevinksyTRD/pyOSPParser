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
from typing import List, Union


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

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        if value in [self.OVERRIDE, self.BIAS, self.RESET]:
            self._action = value
        else:
            raise TypeError('The action should be either "OSPEvent.OVERRIDE", '
                            '"OSPEvent.BIAS" or "OSPEvent.RESET"')

    def to_dict(self):
        return {
            'time': self.time, 'model': self.model,
            'variable': self.variable, 'action': EventAction(self.action).name,
            'value': int(self.value) if int(self.value) == self.value else self.value
        }


class OSPScenario:
    events: List[OSPEvent]

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
        self.events = []

    def add_event(self, event: OSPEvent) -> OSPEvent:
        """Add an event

        Excetions:
            TypeError if the event is not OSPEvent instance
            TypeError if there is already an event that matches time, component and variable
            TypeError if the event time is out of range
        """

        if type(event) is not OSPEvent:
            raise TypeError("The event should be an instance of OSPEvent class")
        if len(self.find_event(
                time=event.time, component=event.model, variable=event.variable
        )) > 0:
            raise TypeError("There is already an event that matches time, component and variable")
        if event.time > self.end or event.time < 0:
            raise TypeError(f"Event time should be greater than 0 and less "
                            f"than the scenario end time {self.end}")
        self.events.append(event)

        return event

    def update_event(
            self,
            time: float,
            component: str,
            variable: str,
            action: int = None,
            value: str = None
    ) -> OSPEvent:
        """Updates an event that matches the arguments given

        One can update action or value or both. If no value is given, then no change is done.

        Exceptions:
             TypeError if no event is found for the keys given or there are multiple events found.
        """
        event = self.find_event(time=time, component=component, variable=variable)
        if len(event) == 1:
            if action:
                event[0].action = action
            if value:
                event[0].value = value
            return event[0]
        else:
            TypeError('No event is found or there are multiple events found')

    def delete_events(self, time: float = None, component: str = None, variable: str = None) -> \
            List[OSPEvent]:
        """Delete events

         If no argument is provided, it deletes all events. Givent the arguments, events
         that match the argument values are found and deleted.
         """
        events = self.find_event(time=time, component=component, variable=variable)
        return [self.events.pop(self.events.index(event)) for event in events]

    def find_event(self, time: float = None, component: str = None, variable: str = None) \
            -> List[OSPEvent]:
        """Find events that matches the given keys"""
        events_found = filter(lambda x: x, self.events)
        if time is not None:
            events_found = filter(lambda x: x.time == time, self.events)
        if component is not None:
            events_found = filter(lambda x: x.model == component, events_found)
        if variable is not None:
            events_found = filter(lambda x: x.variable == variable, events_found)
        return list(events_found)

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
