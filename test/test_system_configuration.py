import json
import os
import random
import string
from typing import Union

import pytest
import xmlschema

from pyOSPParser.system_configuration import PATH_TO_XML_SCHEMA, Value, OspInitialValue, \
    OSP_VARIABLE_CLASS, OspBoolean, OspInteger, OspString, OspReal, OspSimulator, \
    OspVariableEndpoint, OspSignalEndpoint, OspVariableConnection, \
    OspSignalConnection, OspVariableGroupConnection, OspSignalGroupConnection, \
    OspConnections, OspLinearTransformationFunction, OspSumFunction, OspVectorSumFunction, \
    OspFunctions, OspSystemStructure

PATH_TO_TEST_SYSTEM_STRUCTURE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'files',
    'OspSystemStructure_QT_for_parsing_testing.xml'
)


# noinspection PyPep8Naming
def assertEqual(a, b):
    assert a == b


def create_a_random_name(length: int):
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def test_value():
    """Test Value class"""
    #: Test initialization
    with pytest.raises(TypeError):
        Value()
    value = random.random()
    obj = Value(value=value)
    assert value == obj.value
    dict_xml = obj.to_dict_xml()
    assert dict_xml['@value'] == value
    obj = Value(dict_xml=dict_xml)
    assert dict_xml['@value'] == obj.value


def test_osp_initial_value():
    """Test OspInitialValue class"""
    # Test creating the object without any arguments
    with pytest.raises(TypeError):
        OspInitialValue()

    variable_klass = random.choice(list(OSP_VARIABLE_CLASS.values()))
    variable_obj: Union[OspReal, OspString, OspInteger, OspBoolean] = \
        variable_klass(value=random.random())
    variable = create_a_random_name(5)
    obj = OspInitialValue(variable=variable, value=variable_obj)
    assert obj.variable == variable
    assert obj.value == variable_obj
    dict_xml = obj.to_dict_xml()
    assert dict_xml['@variable'] == variable
    assert dict_xml[variable_obj.name] == variable_obj.to_dict_xml()

    # Create from dict_xml
    obj = OspInitialValue(dict_xml=dict_xml)
    assert dict_xml == obj.to_dict_xml()


def test_osp_simulator():
    """Test OspSimulator class"""
    # Test creating the object without any arguments
    with pytest.raises(TypeError):
        OspSimulator()

    # Create a OspSimulator object
    number_initial_values = random.randint(1, 10)
    initial_values = []
    for _ in range(number_initial_values):
        variable_klass = random.choice(list(OSP_VARIABLE_CLASS.values()))
        variable_obj: Union[OspReal, OspString, OspInteger, OspBoolean] = \
            variable_klass(value=random.random())
        initial_values.append(
            OspInitialValue(variable=create_a_random_name(5), value=variable_obj)
        )
    name = create_a_random_name(10)
    source = create_a_random_name(5)
    fmu_rel_path = '%s/' % create_a_random_name(14)
    step_size = random.random()
    obj = OspSimulator(
        name=name, source=source, stepSize=step_size,
        InitialValues=initial_values, fmu_rel_path=fmu_rel_path
    )
    assert obj.name == name
    assert obj.source == source
    assert obj.fmu_rel_path == fmu_rel_path
    assert obj.stepSize == step_size
    assert obj.InitialValues == initial_values
    dict_xml = obj.to_dict_xml()
    assert dict_xml['@name'] == name
    assert dict_xml['@source'] == fmu_rel_path + source
    assert dict_xml['@stepSize'] == step_size
    for i, init_value in enumerate(dict_xml['InitialValues']['InitialValue']):
        assert init_value == initial_values[i].to_dict_xml()
    obj = OspSimulator(dict_xml=dict_xml)
    assert obj.name == name
    assert obj.source == source
    assert obj.fmu_rel_path == fmu_rel_path
    assert obj.stepSize == step_size
    for i, init_value in enumerate(obj.InitialValues):
        assert init_value.to_dict_xml() == initial_values[i].to_dict_xml()


def test_osp_variable_endpoint():
    """Test OspVariableEndpoint class"""
    # Try to create a osp_variable_endpoint obj without giving argument
    with pytest.raises(TypeError):
        OspVariableEndpoint()

    # Create an instance with arguments
    simulator = create_a_random_name(6)
    name = create_a_random_name(8)
    obj = OspVariableEndpoint(
        simulator=simulator, name=name
    )
    assert obj.name == name
    assert obj.simulator == simulator

    # Test to_dict_xml method
    dict_xml = obj.to_dict_xml()
    assert dict_xml['@simulator'] == simulator
    assert dict_xml['@name'] == name

    # Test from_dict_xml method
    obj = OspVariableEndpoint(dict_xml=dict_xml)
    assert obj.to_dict_xml() == dict_xml


def test_signal_endpoint():
    """Test OspSignalEndpoint class"""
    # Try to create a OspSignalEndpoint obj without giving argument
    with pytest.raises(TypeError):
        OspSignalEndpoint()

    # Create an instance with arguments
    function = create_a_random_name(6)
    name = create_a_random_name(8)
    obj = OspSignalEndpoint(function=function, name=name)
    assertEqual(obj.name, name)
    assertEqual(obj.function, function)

    # Test to_dict_xml method
    dict_xml = obj.to_dict_xml()
    assertEqual(dict_xml['@function'], function)
    assertEqual(dict_xml['@name'], name)

    # Test from_dict_xml method
    obj = OspSignalEndpoint(dict_xml=dict_xml)
    assertEqual(obj.to_dict_xml(), dict_xml)


def test_osp_variable_connection():
    """Test OspVariableConnection class"""
    # Try to create a OspVariableConnection obj without giving argument
    with pytest.raises(TypeError):
        OspVariableConnection()

    # Create an instance with arguments
    var_endpoints = [
        OspVariableEndpoint(
            simulator=create_a_random_name(5), name=create_a_random_name(7)
        ) for _ in range(2)
    ]
    obj = OspVariableConnection(Variable=var_endpoints)
    assertEqual(obj.Variable, var_endpoints)

    # Test to_dict_xml method
    dict_xml = obj.to_dict_xml()
    for i, var_endpoint in enumerate(dict_xml['Variable']):
        assertEqual(var_endpoint, var_endpoints[i].to_dict_xml())

    # Test from_dict_xml method
    obj = OspVariableConnection(dict_xml=dict_xml)
    assertEqual(obj.to_dict_xml(), dict_xml)

    # Test with single variable endpoint
    var_endpoints.pop(0)
    with pytest.raises(TypeError):
        OspVariableConnection(Variable=var_endpoints)


def test_osp_signal_connection():
    """
    Test OspSignalConnection class
    """
    # Try to create a OspSignalConnection obj without giving argument
    with pytest.raises(TypeError):
        OspSignalConnection()

    # Create an instance with arguments
    var_endpoint = OspVariableEndpoint(
        simulator=create_a_random_name(5), name=create_a_random_name(7)
    )
    sig_endpoint = OspSignalEndpoint(
        function="Sum", name=create_a_random_name(6)
    )
    obj = OspSignalConnection(Variable=var_endpoint, Signal=sig_endpoint)
    assertEqual(obj.Variable, var_endpoint)
    assertEqual(obj.Signal, sig_endpoint)

    # Test to_dict_xml method
    dict_xml = obj.to_dict_xml()
    assertEqual(dict_xml['Variable'], var_endpoint.to_dict_xml())
    assertEqual(dict_xml['Signal'], sig_endpoint.to_dict_xml())

    # Test from_dict_xml method
    obj = OspSignalConnection(dict_xml=dict_xml)
    assertEqual(obj.to_dict_xml(), dict_xml)


def test_osp_variable_group_connection():
    """Test OspVariableGroupConnection class"""

    # Try to create a OspVariableGroupConnection obj without giving argument
    with pytest.raises(TypeError):
        OspVariableGroupConnection()

    # Create an instance with arguments
    var_group_objs = [
        OspVariableEndpoint(
            simulator=create_a_random_name(5), name=create_a_random_name(7)
        ) for _ in range(2)
    ]
    obj = OspVariableGroupConnection(VariableGroup=var_group_objs)
    assertEqual(obj.VariableGroup, var_group_objs)

    # Test to_dict_xml method
    dict_xml = obj.to_dict_xml()
    for i, var_endpoint in enumerate(dict_xml['VariableGroup']):
        assertEqual(var_endpoint, var_group_objs[i].to_dict_xml())

    # Test from_dict_xml method
    obj = OspVariableGroupConnection(dict_xml=dict_xml)
    assertEqual(obj.to_dict_xml(), dict_xml)

    # Test with single variable endpoint
    var_group_objs.pop(0)
    with pytest.raises(TypeError):
        OspVariableGroupConnection(VariableGroup=var_group_objs)


def test_osp_signal_group_connection():
    """Test OspSignalGroupConnection class"""

    # Try to create a OspSignalGroupConnection obj without giving argument
    with pytest.raises(TypeError):
        OspSignalGroupConnection()

    # Create an instance with arguments
    var_endpoint = OspVariableEndpoint(
        simulator=create_a_random_name(5), name=create_a_random_name(7)
    )
    sig_endpoint = OspSignalEndpoint(
        function="LinearTransformation", name=create_a_random_name(6)
    )
    obj = OspSignalGroupConnection(
        VariableGroup=var_endpoint, SignalGroup=sig_endpoint
    )
    assertEqual(obj.VariableGroup, var_endpoint)
    assertEqual(obj.SignalGroup, sig_endpoint)

    # Test to_dict_xml method
    dict_xml = obj.to_dict_xml()
    assertEqual(dict_xml['VariableGroup'], var_endpoint.to_dict_xml())
    assertEqual(dict_xml['SignalGroup'], sig_endpoint.to_dict_xml())

    # Test from_dict_xml method
    obj = OspSignalGroupConnection(dict_xml=dict_xml)
    assertEqual(obj.to_dict_xml(), dict_xml)


def test_connections():
    """
    Test OspConnections class
    """
    # Create the object without any argument
    OspConnections()

    # Create the object with arguments
    var_conn = []
    for _ in range(random.randint(1, 5)):
        var_endpoint_for_var_conn = [
            OspVariableEndpoint(
                simulator=create_a_random_name(5), name=create_a_random_name(6)
            ) for _ in range(2)
        ]
        var_conn.append(
            OspVariableConnection(Variable=var_endpoint_for_var_conn)
        )
    sig_conn = []
    for _ in range(random.randint(1, 5)):
        sig_endpoint_for_sig_conn = OspSignalEndpoint(
            function="Sum", name=create_a_random_name(7)
        )
        var_endpoint_for_sig_conn = OspVariableEndpoint(
            simulator=create_a_random_name(8),
            name=create_a_random_name(9)
        )
        sig_conn.append(OspSignalConnection(
            Variable=var_endpoint_for_sig_conn,
            Signal=sig_endpoint_for_sig_conn
        ))
    var_group_conn = []
    for _ in range(random.randint(1, 5)):
        var_endpoint_for_var_group_conn = [
            OspVariableEndpoint(
                simulator=create_a_random_name(10),
                name=create_a_random_name(11)
            ) for _ in range(2)
        ]
        var_group_conn.append(OspVariableGroupConnection(
            VariableGroup=var_endpoint_for_var_group_conn
        ))
    sig_group_conn = []
    for _ in range(random.randint(1, 5)):
        sig_endpoint_for_sig_group_conn = OspSignalEndpoint(
            function="Sum", name=create_a_random_name(12)
        )
        var_endpoint_for_sig_group_conn = OspVariableEndpoint(
            simulator=create_a_random_name(13),
            name=create_a_random_name(14)
        )
        sig_group_conn.append(OspSignalGroupConnection(
            SignalGroup=sig_endpoint_for_sig_group_conn,
            VariableGroup=var_endpoint_for_sig_group_conn
        ))
    obj = OspConnections(
        VariableConnection=var_conn,
        SignalConnection=sig_conn,
        VariableGroupConnection=var_group_conn,
        SignalGroupConnection=sig_group_conn
    )
    assertEqual(obj.VariableConnection, var_conn)
    assertEqual(obj.SignalConnection, sig_conn)
    assertEqual(obj.VariableGroupConnection, var_group_conn)
    assertEqual(obj.SignalGroupConnection, sig_group_conn)

    # Test to_dict_xml method
    dict_xml = obj.to_dict_xml()
    for i, each_var_conn in enumerate(dict_xml['VariableConnection']):
        assertEqual(each_var_conn, var_conn[i].to_dict_xml())
    for i, each_var_conn in enumerate(dict_xml['SignalConnection']):
        assertEqual(each_var_conn, sig_conn[i].to_dict_xml())
    for i, each_var_conn in enumerate(dict_xml['VariableGroupConnection']):
        assertEqual(each_var_conn, var_group_conn[i].to_dict_xml())
    for i, each_var_conn in enumerate(dict_xml['SignalGroupConnection']):
        assertEqual(each_var_conn, sig_group_conn[i].to_dict_xml())

    # Test from_dict_xml method
    obj = OspConnections(dict_xml=dict_xml)
    assertEqual(dict_xml, obj.to_dict_xml())


def test_osp_linear_transformation():
    """
    Test OspLinearTransformation class
    """
    # Try to create a OspLinearTransformation obj without giving argument
    with pytest.raises(TypeError):
        OspLinearTransformationFunction()

    # Create an instance with arguments
    name = create_a_random_name(6)
    factor = random.random()
    offset = random.random()
    obj = OspLinearTransformationFunction(name=name, factor=factor, offset=offset)
    assertEqual(obj.name, name)
    assertEqual(obj.factor, factor)
    assertEqual(obj.offset, offset)

    # Test to_dict_xml method
    dict_xml = obj.to_dict_xml()
    assertEqual(dict_xml['@name'], name)
    assertEqual(dict_xml['@factor'], factor)
    assertEqual(dict_xml['@offset'], offset)

    # Test from_dict_xml method
    obj = OspLinearTransformationFunction(dict_xml=dict_xml)
    assertEqual(obj.to_dict_xml(), dict_xml)


def test_osp_sum_function():
    """Test OspSumFunction class"""
    # Try to create a OspSumFunction obj without giving argument
    with pytest.raises(TypeError):
        OspSumFunction()

    # Create an instance with arguments
    name = create_a_random_name(6)
    input_count = random.randint(1, 10)
    obj = OspSumFunction(name=name, inputCount=input_count)
    assertEqual(obj.name, name)
    assertEqual(obj.inputCount, input_count)

    # Test to_dict_xml method
    dict_xml = obj.to_dict_xml()
    assertEqual(dict_xml['@name'], name)
    assertEqual(dict_xml['@inputCount'], input_count)

    # Test from_dict_xml method
    obj = OspSumFunction(dict_xml=dict_xml)
    assertEqual(obj.to_dict_xml(), dict_xml)


def test_osp_vector_sum():
    """Test OspVectorSum class"""

    # Try to create a OspVectorSum obj without giving argument
    with pytest.raises(TypeError):
        OspVectorSumFunction()

    # Create an instance with arguments
    name = create_a_random_name(6)
    input_count = random.randint(1, 10)
    dimension = random.randint(1, 10)
    obj = OspVectorSumFunction(name=name, inputCount=input_count, dimension=dimension)
    assertEqual(obj.name, name)
    assertEqual(obj.inputCount, input_count)
    assertEqual(obj.dimension, dimension)

    # Test to_dict_xml method
    dict_xml = obj.to_dict_xml()
    assertEqual(dict_xml['@name'], name)
    assertEqual(dict_xml['@inputCount'], input_count)
    assertEqual(dict_xml['@dimension'], dimension)

    # Test from_dict_xml method
    obj = OspVectorSumFunction(dict_xml=dict_xml)
    assertEqual(obj.to_dict_xml(), dict_xml)


def test_osp_functions():
    """Test OspFunctions class"""
    # Create the object without any argument
    OspFunctions()

    # Create the object with arguments
    linear_transformation = [
        OspLinearTransformationFunction(
            name=create_a_random_name(5),
            factor=random.random(),
            offset=random.random()
        ) for _ in range(random.randint(1, 5))
    ]
    sum_function = [
        OspSumFunction(
            name=create_a_random_name(6),
            inputCount=random.randint(1, 10)
        ) for _ in range(random.randint(1, 5))
    ]
    vector_sum = [
        OspVectorSumFunction(
            name=create_a_random_name(6),
            inputCount=random.randint(1, 10),
            dimension=random.randint(1, 10)
        ) for _ in range(random.randint(1, 5))
    ]
    obj = OspFunctions(
        LinearTransformation=linear_transformation,
        Sum=sum_function,
        VectorSum=vector_sum
    )
    assertEqual(obj.LinearTransformation, linear_transformation)
    assertEqual(obj.Sum, sum_function)
    assertEqual(obj.VectorSum, vector_sum)

    # Test to_dict_xml method
    dict_xml = obj.to_dict_xml()
    for i, each_func in enumerate(dict_xml['LinearTransformation']):
        assertEqual(each_func, linear_transformation[i].to_dict_xml())
    for i, each_func in enumerate(dict_xml['Sum']):
        assertEqual(each_func, sum_function[i].to_dict_xml())
    for i, each_func in enumerate(dict_xml['VectorSum']):
        assertEqual(each_func, vector_sum[i].to_dict_xml())

    # Test from_dict_xml method
    obj = OspFunctions(dict_xml=dict_xml)
    assertEqual(dict_xml, obj.to_dict_xml())


def test_osp_system_structure():
    # create from a dict_xml
    obj = OspSystemStructure(xml_source=PATH_TO_TEST_SYSTEM_STRUCTURE)
    dict_xml = obj.to_dict_xml()
    xml_str = xmlschema.etree_tostring(
        xmlschema.from_json(json.dumps(dict_xml), obj.xs)
    )
    obj_ref = OspSystemStructure()
    obj_ref.from_xml(xml_str)
    dict_xml_ref = obj_ref.to_dict_xml()
    assertEqual(dict_xml, dict_xml_ref)
