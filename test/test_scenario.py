import random
import string

from pyOSPParser.scenario import OSPEvent, EventAction, OSPScenario


def create_random_str(length: int = 5):
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def create_an_event(
        time: float = None,
        model: str = None,
        variable: str = None,
        action: str = None,
        value: float = None
):
    if time is None:
        time = random.random() * 100
    if model is None:
        model = create_random_str()
    if variable is None:
        variable = create_random_str(7)
    if action is None:
        action = random.choice([action for action in EventAction]).value
    if value is None:
        value = random.random() * 10
    return OSPEvent(
        time=time,
        model=model,
        variable=variable,
        action=action,
        value=value
    )


def test_event():
    time = random.random()
    model = 'model X'
    variable = 'variable X'
    action = random.choice([action for action in EventAction]).value
    value = random.random()

    event = OSPEvent(
        time=time, model=model, variable=variable, action=action, value=value
    )
    event_dict = event.to_dict()

    assert event_dict['time'] == time
    assert event_dict['model'] == model
    assert event_dict['variable'] == variable
    assert event_dict['action'] == EventAction(action).name
    assert event_dict['value'] == value


def test_scenario():
    scenario_end_time = 100
    number_events = random.randint(1, 10)
    models_variables = {
        'model 1': [create_random_str(7) for _ in range(random.randint(1, 5))],
        'model 2': [create_random_str(7) for _ in range(random.randint(1, 5))],
        'model 3': [create_random_str(7) for _ in range(random.randint(1, 5))],
    }

    # Test if OSPScenario object contains the information given
    scenario = OSPScenario(
        name='Test scenario',
        end=scenario_end_time,
        description=create_random_str(50)
    )
    for i in range(number_events):
        model = random.choice(list(models_variables.keys()))
        variable = random.choice(models_variables[model])
        scenario.add_event(create_an_event(model=model, variable=variable))
    scenario_dict = scenario.to_dict()

    assert scenario_dict['end'] == scenario_end_time

    # Check if the to_dict method works properly
    for event in scenario.events:
        assert event.to_dict() in scenario_dict['events']

    # Check if to_json/from_json method works properly
    scenario_json = scenario.to_json()
    scenario.from_json(scenario_json)
    assert scenario_dict['end'] == scenario.end
    assert scenario_dict['description'] == scenario.description
    for event in scenario.events:
        assert event.to_dict() in scenario_dict['events']
