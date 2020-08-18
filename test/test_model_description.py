import json
import os
import random
import string
from typing import List, Dict, Union

import pytest
import xmlschema

from pyOSPParser.model_description import PATH_TO_XML_SCHEMA, get_osp_model_description_type_from_json, \
    OspModelDescription, variable_group_types, OspVariableType, InterfaceError, \
    find_type_of_variable_groups

# Create a path list to osp model description files
fmu_names = ['chassis', 'ground', 'KnuckleBoomCrane', 'wheel']
path_to_test_file_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'files'
)
path_to_osp_model_description_files = [os.path.join(
    path_to_test_file_dir,
    '%s_OspModelDescription.xml' % fmu_name,
) for fmu_name in fmu_names
]
for path in path_to_osp_model_description_files:
    os.path.isfile(path)

# var_group_types
var_group_types = variable_group_types.copy()
var_group_types.pop('Generic')

# import json file for fmus
with open(os.path.join(path_to_test_file_dir, 'fmu.json'), 'rt') as file:
    fmus: List[Dict[str, Union[str, List[str]]]] = json.loads(file.read())

# xml_schema for handling xml files or objects
xml_schema = xmlschema.XMLSchema(PATH_TO_XML_SCHEMA)


def assertEqual(a, b):
    assert a == b


def assertTrue(x):
    assert x


def assertNotEqual(a, b):
    assert a != b


def assertIsNotNone(a):
    assert a is not None


def create_variable_group(
        type_name: str,
        num_input: int,
        num_output: int,
        input_variables: List[str],
        output_variables: List[str],
        name: str = None
):
    if name is None:
        name = ''.join(random.choices(string.ascii_lowercase, k=5))
    #: Create a port variable groups
    if 'Port' in type_name and 'Power' not in type_name:
        #: Make a random selection of the variables
        num_var_selected = random.randint(1, min(num_input, num_output))
        inputs_selected = random.sample(input_variables, k=num_var_selected)
        outputs_selected = random.sample(output_variables, k=num_var_selected)

        osp_variables_input = [OspVariableType(ref=var, unit='X') for var in inputs_selected]
        osp_variables_output = [OspVariableType(ref=var, unit='Y') for var in outputs_selected]

        fields = [field for field in var_group_types[type_name]['field']]
        variables_pair = [
            var_group_types[fields[0]]['class'](
                name=''.join(random.choices(string.ascii_lowercase, k=5)),
                Variable=osp_variables_input
            ),
            var_group_types[fields[1]]['class'](
                name=''.join(random.choices(string.ascii_lowercase, k=5)),
                Variable=osp_variables_output
            ),
        ]
        dict_xml = {
            '@name': name,
            fields[0]: variables_pair[0].to_dict_xml(),
            fields[1]: variables_pair[1].to_dict_xml(),
        }
        return var_group_types[type_name]['class'](dict_xml=dict_xml)

    #: Create a variable group
    else:
        #: Choose randomly between inputs and outputs
        variables = input_variables if random.random() > 0.5 else output_variables
        osp_variables = [OspVariableType(ref=var, unit='X') for var in variables]
        return var_group_types[type_name]['class'](
            name=name,
            Variable=osp_variables
        )


def get_fmu_inputs_and_outputs(fmu_name):
    fmu = list(filter(lambda x: x.get('name') == fmu_name, fmus))[0]
    input_variables = fmu.get('inputs')
    output_variables = fmu.get('outputs')
    return input_variables, output_variables


def test_parsing_and_json_convert():
    for i, path_osp in enumerate(path_to_osp_model_description_files):
        #: Get the data in json format
        dict_xml = xml_schema.to_dict(path_osp)
        osp_model_description = OspModelDescription(xml_source=path_osp)
        xml_string_converted = osp_model_description.to_xml_str()
        dict_xml_comp = xml_schema.to_dict(xml_string_converted)
        fields_to_compare = ['UnitDefinitions', 'VariableGroups', 'version']
        for field in fields_to_compare:
            assertEqual(dict_xml.get(field, None), dict_xml_comp.get(field, None))


def test_add_interface():
    for i, path_osp in enumerate(path_to_osp_model_description_files):

        #: Create the OspModelDescriptionType instance
        dict_xml = xml_schema.to_dict(path_osp)
        osp_model_description_obj = OspModelDescription(dict_xml=dict_xml)

        #: Add an arbitrary interface
        number_interfaces_to_add = 5
        var_group_types = variable_group_types.copy()
        var_group_types.pop('Generic')
        list_variable_groups = list(var_group_types.keys())

        types_chosen = random.choices(list_variable_groups, k=number_interfaces_to_add)
        interfaces = []

        fmu_name = os.path.splitext(os.path.basename(path_osp))[0]
        fmu_name = fmu_name[:fmu_name.index('_')]
        input_variables, output_variables = get_fmu_inputs_and_outputs(fmu_name)

        for j, type_name in enumerate(types_chosen):
            #: Randomly decide if a variable group will be an input or output
            num_input = len(input_variables)
            num_output = len(output_variables)

            interfaces.append(create_variable_group(
                type_name=type_name,
                num_input=num_input,
                num_output=num_output,
                input_variables=input_variables,
                output_variables=output_variables
            ))

            variable_group_before_add = osp_model_description_obj.VariableGroups.__getattribute__(type_name)
            variable_group_before_add = [] if variable_group_before_add is None else variable_group_before_add.copy()

            osp_model_description_obj.add_interface(interfaces[j])

            variable_group_after_add = osp_model_description_obj.VariableGroups.__getattribute__(type_name)

            assertEqual(len(variable_group_before_add) + 1, len(variable_group_after_add))
            assertEqual(variable_group_after_add[-1], interfaces[j])

        #: add an interface with the same name
        name = interfaces[0].name
        type_name = random.choice(list_variable_groups)
        interface_with_the_same_name = create_variable_group(
            name=name,
            type_name=type_name,
            num_input=1,
            num_output=1,
            input_variables=input_variables,
            output_variables=output_variables
        )
        with pytest.raises(InterfaceError):
            osp_model_description_obj.add_interface(interface_with_the_same_name)


def test_update_delete_interface():
    list_variable_groups = [var_group_name for var_group_name in variable_group_types]
    list_variable_groups.remove('Generic')

    for i, path_osp in enumerate(path_to_osp_model_description_files):
        #: Create the OspModelDescriptionType instance
        dict_xml = xml_schema.to_dict(path_osp)
        osp_model_description_obj = OspModelDescription(dict_xml=dict_xml)

        #: Select a random interface and update it
        interfaces = []
        for var_group_type in variable_group_types:
            var_group = osp_model_description_obj.VariableGroups.__getattribute__(var_group_type)
            if var_group is not None:
                for var in var_group:
                    interfaces.append(var)

        var_group_selected = random.choice(interfaces)
        type_name = random.choice(list_variable_groups)
        fmu_name = os.path.splitext(os.path.basename(path_osp))[0]
        fmu_name = fmu_name[:fmu_name.index('_')]
        input_variables, output_variables = get_fmu_inputs_and_outputs(fmu_name)
        new_interface = create_variable_group(
            type_name=type_name,
            num_input=1,
            num_output=1,
            input_variables=input_variables,
            output_variables=output_variables
        )

        osp_model_description_obj.update_interface(new_interface, old_name=var_group_selected.name)

        #: Check if the old interface to be updated has been removed
        type_name = find_type_of_variable_groups(var_group_selected)
        var_groups = osp_model_description_obj.VariableGroups.__getattribute__(type_name)
        if var_groups is not None:
            for var in var_groups:
                assertNotEqual(var.name, var_group_selected.name)

        #: Check
        type_name = find_type_of_variable_groups(new_interface)
        var_groups_updated = osp_model_description_obj.VariableGroups.__getattribute__(type_name)
        assertIsNotNone(var_groups_updated)
        matched = False
        for var in var_groups_updated:
            matched |= var.name == new_interface.name
        assertTrue(matched)
