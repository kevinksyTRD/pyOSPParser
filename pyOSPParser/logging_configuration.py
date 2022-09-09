""" Contains classes for creating, importing and deploying
a logging configuration for co-simulation from Open Simulation Platform

Classes
    OSPVariableForLogging: Class for variable for logging in OSP scenario

    OSPSimulatorForLogging: Class for simulator for logging that contains
    collection of OSPVariableForLogging instances

    OSPLoggingConfiguration: Class for logging configuration that contains
    collection of OSPSimulatorForLogging instances

Attributes:
    PATH_TO_XML_SCHEMA_FOR_LOGGING(str): file path for the XML schema file for
    logging configuration.

"""

import json
import os
from abc import ABC, abstractmethod
from typing import List, Union, Dict

import xmlschema

PATH_TO_XML_SCHEMA_FOR_LOGGING = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'xmlschema',
    'LoggingConfiguration.xsd'
)


class OspLoggingConfigurationAbstract(ABC):
    @property
    @abstractmethod
    def _required_keys(self):
        pass

    def __init__(self, dict_xml: Union[Dict, None] = None, **kwargs):
        if dict_xml:
            self.from_dict_xml(dict_xml)
        else:
            for key in self._required_keys:
                if key in kwargs:
                    self.__setattr__(key, kwargs[key])
                else:
                    msg = "A required argument, '%s', is missing" % key
                    raise TypeError(msg)
            for key, value in kwargs.items():
                if key not in self._required_keys:
                    self.__setattr__(key, value)

    @abstractmethod
    def to_dict_xml(self):
        """This method should be defined for the inherited class"""
        return {}

    @abstractmethod
    def from_dict_xml(self, dict_xml: Dict):
        """This method should be defined for the inherited class"""


class OspVariableForLogging(OspLoggingConfigurationAbstract):
    name: str
    _required_keys = ['name']

    def __init__(self, dict_xml: Union[Dict, None] = None, **kwargs):
        """Constructor for OspVariableForLogging class
        One should provide either 'dict_xml', a dictionary that contains the information of the instance, or
        'name', the name of variable.

        Args:
            name (str, optional): Name of the variable to log.
            dict_xml (Dict[str, str], optional): XML content of the instance to create the instance from.
        """
        super().__init__(dict_xml, **kwargs)

    def to_dict_xml(self):
        return {'@name': self.name}

    def from_dict_xml(self, dict_xml: Dict):
        self.name = dict_xml['@name']


class OspSimulatorForLogging(OspLoggingConfigurationAbstract):
    """Class for a simulator instance for logging configuration"""
    name: str
    decimation_factor: int = None
    variables: List[OspVariableForLogging]
    _required_keys = ['name']

    def __init__(self, dict_xml: Union[Dict, None] = None, **kwargs):
        """Constructor for OspSimulatorForLogging class

        "name" and "variables" arguments are required. Otherwise, one can
        provide the dictionary to create one.

        Args:
            name(str): Name of the simulator
            variables(List[OspVariableForLogging]: Sampling rate of the
                simulation results. For example, decimationFactor=1 means the
                results of every simulation step of the simulator are logged.
                And decimationFactor=10 means every 10th of the simulation
                results are logged.
            dict_xml(Dict): A dictionary that contains the information of the

        """
        self.variables = []
        super(OspSimulatorForLogging, self).__init__(dict_xml, **kwargs)
        variables = kwargs.get('variables', None)
        if variables is not None:
            if type(variables) is not list:
                raise TypeError('Variables should be a list of OspVariableForLogging instances')
            for variable in variables:
                if type(variable) is not OspVariableForLogging:
                    raise TypeError('Variables should be a list of OspVariableForLogging instances.')
            self.variables = variables
        if self.decimation_factor is None:
            self.decimation_factor = 1

    def to_dict_xml(self):
        """Export a dictionary that contains the information of the instance"""
        return {
            '@name': self.name,
            '@decimationFactor': self.decimation_factor,
            'variable': [variable.to_dict_xml() for variable in self.variables]
        }

    def from_dict_xml(self, dict_xml: Dict):
        """Import a dictionary that contains the information of the instance"""
        self.name = dict_xml['@name']
        self.decimation_factor = dict_xml.get('@decimationFactor', 1)
        self.variables = [OspVariableForLogging(dict_xml=variable) for variable in dict_xml.get('variable', [])]

    def add_variable(self, variable: str):
        """Add a variable

        Args:
            variable: Name of a variable to add.
        """
        self.variables.append(OspVariableForLogging(name=variable))


class OspLoggingConfiguration(OspLoggingConfigurationAbstract):
    simulators: Union[List[OspSimulatorForLogging], None] = None
    _required_keys = []

    def __init__(self, dict_xml: Dict = None, xml_source: str = None, **kwargs):
        """Constructor for OspLoggingConfiguration class

        Args:
            dict_xml(Dict, optional): A dictionary that contains the information of the instance.
            xml_source(str, optional): File path or String content of XML to import the logging configuration
            simulators(List[OspSimulatorForLogging], optional): A list of OspSimulatorForLogging instances

        """
        if xml_source is not None:
            self.from_xml_str(xml_source)
        else:
            super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        """Export a dictionary that contains the information of the instance"""
        return {'@xmlns': 'http://opensimulationplatform.com/LogConfig',
                'simulator': [simulator.to_dict_xml() for simulator in self.simulators]}

    def from_dict_xml(self, dict_xml: Dict):
        """Import a dictionary that contains the information of the instance"""
        self.simulators = [
            OspSimulatorForLogging(dict_xml=simulator) for simulator in dict_xml.get('simulator', [])
        ]

    def to_xml_str(self) -> str:
        """Convert the instance to XML string"""
        xs = xmlschema.XMLSchema(PATH_TO_XML_SCHEMA_FOR_LOGGING)
        json_text = json.dumps(self.to_dict_xml(), indent=2)
        et = xmlschema.from_json(json_text, xs)

        xml_str = xmlschema.etree_tostring(et)
        namespace = xmlschema.XMLResource(PATH_TO_XML_SCHEMA_FOR_LOGGING).get_namespaces()['']
        xml_str = xml_str.replace('xmlns="%s"' % namespace, '')

        return xml_str

    def from_xml_str(self, xml_source: str):
        """Imports logging configuration file

        Args:
            xml_source(str): File path or string content of XML file to import
        """
        xs = xmlschema.XMLSchema(PATH_TO_XML_SCHEMA_FOR_LOGGING)
        if os.path.isfile(xml_source):
            with open(xml_source, 'rt') as file:
                xml_str = file.read()
        else:
            xml_str = xml_source
        namespace = xmlschema.XMLResource(
            PATH_TO_XML_SCHEMA_FOR_LOGGING).get_namespaces()['']
        xml_str = xml_str.replace('<simulators', '<simulators xmlns="%s" ' % namespace)
        if xs.is_valid(xml_str):
            xml_dict = xs.to_dict(xml_str)
            self.from_dict_xml(xml_dict)
        else:
            xs.validate(xml_str)

    def set_decimation_factor(self, component_name: str, decimation_factor: int):
        """Sets a value for decimation factor for a component"""
        try:
            simulator = next(
                simulator for simulator in self.simulators if simulator.name == component_name
            )
        except StopIteration:
            NameError(f'No configuration is found for the component {component_name}')
        simulator.decimation_factor = int(decimation_factor)
