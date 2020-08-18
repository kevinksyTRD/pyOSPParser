import random
import string

from pyOSPParser.logging_configuration import OspVariableForLogging, \
    OspSimulatorForLogging, OspLoggingConfiguration


def create_random_str(length: int = 5):
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def create_a_variable(
        name: str = None
):
    if name is None:
        name = create_random_str(5)
    return OspVariableForLogging(name=name)


def test_variable_for_logging():
    # Test to_dict
    name = create_random_str(5)
    variable = create_a_variable(name)
    variable_dict = variable.to_dict_xml()
    assert variable_dict['@name'] == name

    # Test from_dict
    variable_copy = OspVariableForLogging(dict_xml=variable_dict)
    variable_dict_copy = variable_copy.to_dict_xml()

    assert variable_dict == variable_dict_copy


def test_simulation_for_logging():
    # Create a simulator for logging instance
    number_variables = random.randint(1, 5)
    variables = [create_a_variable() for _ in range(number_variables)]
    simulator_name = create_random_str(7)
    decimation_factor = random.randint(1, 10)

    simulator = OspSimulatorForLogging(
        name=simulator_name,
        decimation_factor=decimation_factor,
        variables=variables
    )

    # Test to_dict
    simulator_dict_xml = simulator.to_dict_xml()

    assert simulator_dict_xml['@name'] == simulator_name
    assert simulator_dict_xml['@decimationFactor'] == decimation_factor
    for variable in variables:
        assert variable.to_dict_xml() in simulator_dict_xml['variable']

    # Test from_dict
    simulator_copy = OspSimulatorForLogging(dict_xml=simulator_dict_xml)
    simulator_copy_dict_xml = simulator_copy.to_dict_xml()

    assert simulator_dict_xml == simulator_copy_dict_xml


def test_logging_config():
    number_simulators = random.randint(1, 5)
    simulator_names = [create_random_str(5) for _ in range(number_simulators)]
    simulators = []
    for simulator_name in simulator_names:
        variables = [create_a_variable() for _ in range(random.randint(1, 5))]
        decimation_factor = random.randint(1, 10) if random.random() > 0.5 else None
        simulators.append(OspSimulatorForLogging(
            name=simulator_name,
            decimation_factor=decimation_factor,
            variables=variables
        ))

    logging_config = OspLoggingConfiguration(simulators=simulators)
    logging_config_dict_xml = logging_config.to_dict_xml()
    logging_config_xml_str = logging_config.to_xml_str()

    logging_config_copy = OspLoggingConfiguration(xml_source=logging_config_xml_str)
    logging_config_copy_dict_xml = logging_config_copy.to_dict_xml()

    assert logging_config_dict_xml == logging_config_copy_dict_xml
