import random
import string

import pytest

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

    # Test if wrong value for action causes an error
    with pytest.raises(TypeError):
        OSPEvent(time=time, model=model, variable=variable, action=4, value=value)


@pytest.fixture
def scenario() -> OSPScenario:
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
    return scenario


def test_scenario(scenario):
    """Test Scenario for the serializing to create an XML file"""
    scenario_dict = scenario.to_dict()

    assert scenario_dict['end'] == scenario.end

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


def test_add_duplicate_event(scenario):
    """Test adding an event that has the same time, component name and variable name."""
    event_duplicate: OSPEvent = random.choice(scenario.events)
    event_to_be_added = OSPEvent(
        time=event_duplicate.time,
        model=event_duplicate.model,
        variable=event_duplicate.variable,
        action=random.choice([1, 2, 3]),
        value=random.random()
    )
    with pytest.raises(TypeError):
        scenario.add_event(event_to_be_added)


def test_add_event_with_time_out_of_range(scenario):
    """Test adding an event with time that is out of range."""
    event_to_be_added = create_an_event(time=scenario.end * 1.5)
    with pytest.raises(TypeError):
        scenario.add_event(event_to_be_added)
    event_to_be_added.time = -1.0
    with pytest.raises(TypeError):
        scenario.add_event(event_to_be_added)
    event_to_be_added.time = random.random() * scenario.end
    scenario.add_event(event_to_be_added)


def test_find_event(scenario):
    """Test finding an event for a scenario"""
    all_model_names = [event.model for event in scenario.events]
    all_variable_names = [event.variable for event in scenario.events]
    all_time = [event.time for event in scenario.events]
    all_model_names_unique = list(dict.fromkeys(all_model_names).keys())
    all_variable_names_unique = list(dict.fromkeys(all_variable_names).keys())
    all_time_unique = list(dict.fromkeys(all_time).keys())
    model_name = random.choice(all_model_names_unique)
    variable_name = random.choice(all_variable_names_unique)
    time = random.choice(all_time_unique)

    # Only with component
    events_found = scenario.find_event(component=model_name)
    number_counts_ref = sum(map(lambda x: x == model_name, all_model_names))
    assert len(events_found) == number_counts_ref
    assert all(map(lambda x: x.model == model_name, events_found))

    # Only with time
    events_found = scenario.find_event(time=time)
    number_counts_ref = sum(map(lambda x: x == time, all_time))
    assert len(events_found) == number_counts_ref
    assert all(map(lambda x: x.time == time, events_found))

    # Only with variable name
    events_found = scenario.find_event(variable=variable_name)
    number_counts_ref = sum(map(lambda x: x == variable_name, all_variable_names))
    assert len(events_found) == number_counts_ref
    assert all(map(lambda x: x.variable == variable_name, events_found))

    # Combination
    events_found = scenario.find_event(component=model_name, variable=variable_name)
    number_counts_ref = sum(map(
        lambda event: event.model == model_name and
        event.variable == variable_name, scenario.events
    ))
    assert len(events_found) == number_counts_ref
    assert all(map(
        lambda event: event.variable == variable_name and event.model == model_name, events_found
    ))


def test_delete_events_all(scenario):
    """Test deleting all events"""
    assert len(scenario.events) > 0
    scenario.delete_events()
    assert len(scenario.events) == 0


def test_delete_events_by_a_key(scenario):
    """Test deleting events by a single key"""
    decision = random.random()
    if decision < 0.33:
        key = 'time'
    elif decision < 0.66:
        key = 'model'
    else:
        key = 'variable'
    all_with_the_key = [getattr(event, key) for event in scenario.events]
    all_unique = list(dict.fromkeys(all_with_the_key).keys())
    chosen = random.choice(all_unique)
    if key == 'time':
        scenario.delete_events(time=chosen)
        assert len(scenario.find_event(time=chosen)) == 0
    elif key == 'model':
        scenario.delete_events(component=chosen)
        assert len(scenario.find_event(component=chosen)) == 0
    else:
        scenario.delete_events(variable=chosen)
        assert len(scenario.find_event(variable=chosen)) == 0


def test_delete_event_combination(scenario):
    """Test deleting an event by providing the key arguments"""
    event_to_delete = random.choice(scenario.events)
    num_events_before = len(scenario.events)
    assert scenario.events.index(event_to_delete) >= 0
    scenario.delete_events(
        time=event_to_delete.time,
        component=event_to_delete.model,
        variable=event_to_delete.variable
    )
    assert len(scenario.events) == num_events_before - 1
    with pytest.raises(ValueError):
        scenario.events.index(event_to_delete)


def test_update_event(scenario):
    """Test updating an event by providing the key argument"""
    event_to_update = random.choice(scenario.events)
    time = event_to_update.time
    component_name = event_to_update.model
    variable = event_to_update.variable
    new_action = random.randint(1, 3)
    new_value = random.random()
    scenario.update_event(
        time=time,
        component=component_name,
        variable=variable,
        action=new_action,
        value=new_value
    )
    event = scenario.find_event(time=time, component=component_name, variable=variable)[0]
    assert event.action == new_action
    assert event.value == new_value
