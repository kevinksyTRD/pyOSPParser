import json
import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Union, Dict

import xmlschema

PATH_TO_XML_SCHEMA = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'xmlschema',
    'OspSystemStructure.xsd'
)


class VariableType(Enum):
    Real = 'Real'
    Integer = 'Integer'
    String = 'String'
    Boolean = 'Boolean'


class InterfaceType(Enum):
    Variable = 'VariableConnection'
    Signal = 'SignalConnection'
    VariableGroup = 'VariableGroupConnection'
    SignalGroup = "SignalGroupConnection"


class InterfaceSubType(Enum):
    Bond = 'BondConnection'
    PlugSocket = 'PlugSocketConnection'
    Scalar = 'ScalarConnection'
    Sum = 'SumConnection'


class OspSystemStructureAbstract(ABC):
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
        """
        This method should be defined for the inherited class
        """
        return {}

    @abstractmethod
    def from_dict_xml(self, dict_xml: Dict):
        """
        This method should be defined for the inherited class
        """


class Value(OspSystemStructureAbstract):
    value: Union[None, int, str, bool, float]
    _required_keys = ['value']

    def __init__(self, dict_xml: Dict = None, **kwargs):
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        return {'@value': self.value}

    def from_dict_xml(self, dict_xml):
        self.value = dict_xml['@value']


class OspInteger(Value):
    """
    The "name" member is used in other application. Please make sure that
    the value is not changed without cross-checking
    """
    value: int
    name = 'Integer'


class OspBoolean(Value):
    """
    The "name" member is used in other application. Please make sure that
    the value is not changed without cross-checking
    """
    value: bool
    name = 'Boolean'


class OspString(Value):
    """
    The "name" member is used in other application. Please make sure that
    the value is not changed without cross-checking
    """
    value: str
    name = 'String'


class OspReal(Value):
    """
    The "name" member is used in other application. Please make sure that
    the value is not changed without cross-checking
    """
    value: float
    name = 'Real'


class OspInitialValue(OspSystemStructureAbstract):
    variable: str
    value: Union[OspReal, OspInteger, OspBoolean, OspString]
    _required_keys = ['variable', 'value']

    def __init__(self, dict_xml=None, **kwargs):
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        return {
            '@variable': self.variable,
            self.value.name: self.value.to_dict_xml()
        }

    def from_dict_xml(self, dict_xml):
        self.variable = dict_xml['@variable']
        for var_type in VariableType:
            if var_type.value in dict_xml:
                self.value = OSP_VARIABLE_CLASS[var_type](
                    dict_xml=dict_xml[var_type.value]
                )
                break


class OspSimulator(OspSystemStructureAbstract):
    name: str
    source: str
    stepSize: float = None
    InitialValues: Union[List[OspInitialValue], None] = None
    fmu_rel_path: str = ''
    _required_keys = ['name', 'source']

    def __init__(self, dict_xml=None, **kwargs):
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        dict_xml = {
            '@name': self.name,
            '@source': '%s%s' % (self.fmu_rel_path, self.source),
        }
        if self.stepSize is not None:
            dict_xml['@stepSize'] = self.stepSize
        if self.InitialValues is not None:
            dict_xml['InitialValues'] = {'InitialValue': []}
            for initial_value in self.InitialValues:
                dict_xml['InitialValues']['InitialValue'].append(
                    initial_value.to_dict_xml()
                )
        return dict_xml

    def from_dict_xml(self, dict_xml):
        self.name = dict_xml['@name']
        try:
            idx = dict_xml['@source'].rindex('/')
            self.source = dict_xml['@source'][idx+1:]
            self.fmu_rel_path = dict_xml['@source'][:idx+1]
        except ValueError:
            self.source = dict_xml['@source']
            self.fmu_rel_path = ''
        if '@stepSize' in dict_xml:
            self.stepSize = dict_xml['@stepSize']
        if 'InitialValues' in dict_xml:
            self.InitialValues = []
            for init_value in dict_xml['InitialValues']['InitialValue']:
                self.InitialValues.append(OspInitialValue(dict_xml=init_value))


class OspVariableEndpoint(OspSystemStructureAbstract):
    simulator: str
    name: str
    _required_keys = ['simulator', 'name']

    def __init__(self, dict_xml: Union[Dict, None] = None, **kwargs):
        """
        "simulator" and "name" arguments are required. Unless, one can
        provide the dictionary to create one.
        """
        super().__init__(dict_xml, **kwargs)

    def to_dict_xml(self):
        return {
            '@simulator': self.simulator,
            '@name': self.name
        }

    def from_dict_xml(self, dict_xml: Dict):
        for key in self._required_keys:
            self.__setattr__(key, dict_xml['@%s' % key])


class OspSignalEndpoint(OspSystemStructureAbstract):
    function: str
    name: str
    _required_keys = ['function', 'name']

    def __init__(self, dict_xml: Union[Dict, None] = None, **kwargs):
        """
        "function" and "name" arguments are required. Otherwise, one can
        provide the dictionary to create one.
        """
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        return {
            '@function': self.function,
            '@name': self.name
        }

    def from_dict_xml(self, dict_xml: Dict):
        for key in self._required_keys:
            self.__setattr__(key, dict_xml['@%s' % key])


class OspVariableConnection(OspSystemStructureAbstract):
    Variable: List[OspVariableEndpoint]
    _required_keys = ['Variable']

    def __init__(self, dict_xml: Union[Dict, None] = None, **kwargs):
        """
        "Variable" argument is required. Otherwise, one can
        provide the dictionary to create one.
        """
        super().__init__(dict_xml=dict_xml, **kwargs)
        if len(self.Variable) != 2:
            msg = "Only two variable endpoints are allowed."
            raise TypeError(msg)

    def to_dict_xml(self):
        return {'Variable': [var.to_dict_xml() for var in self.Variable]}

    def from_dict_xml(self, dict_xml: Dict):
        self.Variable = []
        for var in dict_xml['Variable']:
            self.Variable.append(OspVariableEndpoint(dict_xml=var))


class OspSignalConnection(OspSystemStructureAbstract):
    Variable: OspVariableEndpoint
    Signal: OspSignalEndpoint
    _required_keys = ['Variable', 'Signal']

    def __init__(self, dict_xml: Union[Dict, None] = None, **kwargs):
        """
        "Variable" and "Signal" arguments are required. Otherwise, one can
        provide the dictionary to create one.
        """
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        return {
            'Variable': self.Variable.to_dict_xml(),
            'Signal': self.Signal.to_dict_xml()
        }

    def from_dict_xml(self, dict_xml: Dict):
        self.Variable = OspVariableEndpoint(dict_xml=dict_xml['Variable'])
        self.Signal = OspSignalEndpoint(dict_xml=dict_xml['Signal'])


class OspVariableGroupConnection(OspSystemStructureAbstract):
    VariableGroup = List[OspVariableEndpoint]
    _required_keys = ['VariableGroup']

    def __init__(self, dict_xml: Union[Dict, None] = None, **kwargs):
        """
        "VariableGroup" argument is required. Otherwise, one can
        provide the dictionary to create one.
        """
        super().__init__(dict_xml=dict_xml, **kwargs)
        if len(self.VariableGroup) != 2:
            msg = "Only two variable endpoints are allowed."
            raise TypeError(msg)

    def to_dict_xml(self):
        return {
            'VariableGroup': [var_group.to_dict_xml() for var_group in self.VariableGroup]
        }

    def from_dict_xml(self, dict_xml: Dict):
        self.VariableGroup = []
        for var_group in dict_xml['VariableGroup']:
            self.VariableGroup.append(OspVariableEndpoint(dict_xml=var_group))


class OspSignalGroupConnection(OspSystemStructureAbstract):
    SignalGroup: OspSignalEndpoint
    VariableGroup: OspVariableEndpoint
    _required_keys = ['SignalGroup', 'VariableGroup']

    def __init__(self, dict_xml: Union[Dict, None] = None, **kwargs):
        """
        "Variable" and "Signal" arguments are required. Otherwise, one can
        provide the dictionary to create one.
        """
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        return {
            'SignalGroup': self.SignalGroup.to_dict_xml(),
            'VariableGroup': self.VariableGroup.to_dict_xml()
        }

    def from_dict_xml(self, dict_xml: Dict):
        self.VariableGroup = OspVariableEndpoint(dict_xml=dict_xml['VariableGroup'])
        self.SignalGroup = OspSignalEndpoint(dict_xml=dict_xml['SignalGroup'])


class OspConnections(OspSystemStructureAbstract):
    VariableConnection: Union[None, List[OspVariableConnection]] = None
    SignalConnection: Union[None, List[OspSignalConnection]] = None
    VariableGroupConnection: Union[None, List[OspVariableGroupConnection]] = None
    SignalGroupConnection: Union[None, List[OspSignalGroupConnection]] = None
    _required_keys = []

    def __init__(self, dict_xml: Union[Dict, None] = None, **kwargs):
        """
        You can provide the arguments for "VariableConnection", "SignalConnection",
        "VariableGroupConnection" or "SignalGroupConnection". Or the structure can
        be given as a dictionary with these arguments as keys.
        """
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self) -> Union[None, Dict[str, List[Dict]]]:
        dict_xml = {}
        if self.VariableConnection:
            dict_xml['VariableConnection'] = [
                conn.to_dict_xml() for conn in self.VariableConnection
            ]
        if self.SignalConnection:
            dict_xml['SignalConnection'] = [
                conn.to_dict_xml() for conn in self.SignalConnection
            ]
        if self.VariableGroupConnection:
            dict_xml['VariableGroupConnection'] = [
                conn.to_dict_xml() for conn in self.VariableGroupConnection
            ]
        if self.SignalGroupConnection:
            dict_xml['SignalGroupConnection'] = [
                conn.to_dict_xml() for conn in self.SignalGroupConnection
            ]
        if len(dict_xml) == 0:
            dict_xml = None
        return dict_xml

    def from_dict_xml(self, dict_xml: Dict):
        if 'VariableConnection' in dict_xml:
            self.VariableConnection = [
                OspVariableConnection(dict_xml=var_conn)
                for var_conn in dict_xml['VariableConnection']
            ]
        if 'SignalConnection' in dict_xml:
            self.SignalConnection = [
                OspSignalConnection(dict_xml=var_conn)
                for var_conn in dict_xml['SignalConnection']
            ]
        if 'VariableGroupConnection' in dict_xml:
            self.VariableGroupConnection = [
                OspVariableGroupConnection(dict_xml=var_conn)
                for var_conn in dict_xml['VariableGroupConnection']
            ]
        if 'SignalGroupConnection' in dict_xml:
            self.SignalGroupConnection = [
                OspSignalGroupConnection(dict_xml=var_conn)
                for var_conn in dict_xml['SignalGroupConnection']
            ]

    def add_connection(
            self,
            connection: Union[
                OspVariableConnection,
                OspSignalConnection,
                OspVariableGroupConnection,
                OspSignalGroupConnection
            ]
    ):
        if type(connection) is OspVariableConnection:
            self.VariableConnection.append(connection)
        elif type(connection) is OspSignalConnection:
            self.SignalConnection.append(connection)
        elif type(connection) is OspVariableGroupConnection:
            self.VariableGroupConnection.append(connection)
        elif type(connection) is OspSignalGroupConnection:
            self.SignalGroupConnection.append(connection)
        else:
            msg = 'The type of the connections should be either "OspVariableConnection", ' \
                  '"OspSignalConnection", "OspVariableGroupConnection" or "OspSignalGroupConnection"'
            raise TypeError(msg)


class OspLinearTransformationFunction(OspSystemStructureAbstract):
    name: str
    factor: float
    offset: float
    _required_keys = ['name', 'factor', 'offset']

    def __init__(self, dict_xml: Union[Dict, None] = None, **kwargs):
        """
        "name", "factor" and "offset" arguments are required. Otherwise,
        a dictionary with the keys of these arguments can be provided.
        """
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        return {
            '@name': self.name,
            '@factor': self.factor,
            '@offset': self.offset
        }

    def from_dict_xml(self, dict_xml: Dict):
        for key in self._required_keys:
            self.__setattr__(key, dict_xml['@%s' % key])


class OspSumFunction(OspSystemStructureAbstract):
    name: str
    inputCount: int
    _required_keys = ['name', 'inputCount']

    def __init__(self, dict_xml: Union[Dict, None] = None, **kwargs):
        """
        "name", and "inputCount" arguments are required. Otherwise,
        a dictionary with the keys of these arguments can be provided.
        """
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        return {
            '@name': self.name,
            '@inputCount': self.inputCount
        }

    def from_dict_xml(self, dict_xml: Dict):
        for key in self._required_keys:
            self.__setattr__(key, dict_xml['@%s' % key])


class OspVectorSumFunction(OspSystemStructureAbstract):
    name: str
    inputCount = int
    dimension = int
    _required_keys = ['name', 'inputCount', 'dimension']

    def __init__(self, dict_xml: Union[Dict, None] = None, **kwargs):
        """
        "name", "inputCount" and "dimension" arguments are required.
        Otherwise, a dictionary with the keys of these arguments can
        be provided.
        """
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        return {
            '@name': self.name,
            '@inputCount': self.inputCount,
            '@dimension': self.dimension
        }

    def from_dict_xml(self, dict_xml: Dict):
        for key in self._required_keys:
            self.__setattr__(key, dict_xml['@%s' % key])


class OspFunctions(OspSystemStructureAbstract):
    LinearTransformation: Union[None, List[OspLinearTransformationFunction]] = None
    Sum: Union[None, List[OspSumFunction]] = None
    VectorSum: Union[None, List[OspVectorSumFunction]] = None
    _required_keys = []

    def __init__(self, dict_xml: Union[Dict, None] = None, **kwargs):
        """
        "LinearTransformation", "Sum" and "VectorSum" arguments can be provided.
        Otherwise, a dictionary with the keys of these arguments can
        be provided.
        """
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        dict_xml = {}
        if self.LinearTransformation:
            dict_xml['LinearTransformation'] = [
                function.to_dict_xml() for function in self.LinearTransformation
            ]
        if self.Sum:
            dict_xml['Sum'] = [
                function.to_dict_xml() for function in self.Sum
            ]
        if self.VectorSum:
            dict_xml['VectorSum'] = [
                function.to_dict_xml() for function in self.VectorSum
            ]
        if len(dict_xml) == 0:
            dict_xml = None
        return dict_xml

    def from_dict_xml(self, dict_xml: Dict):
        if 'LinearTransformation' in dict_xml:
            self.LinearTransformation = [
                OspLinearTransformationFunction(dict_xml=function)
                for function in dict_xml['LinearTransformation']
            ]
        if 'Sum' in dict_xml:
            self.Sum = [
                OspSumFunction(dict_xml=function)
                for function in dict_xml['Sum']
            ]
        if 'VectorSum' in dict_xml:
            self.VectorSum = [
                OspVectorSumFunction(dict_xml=function)
                for function in dict_xml['VectorSum']
            ]


class OspSystemStructure(OspSystemStructureAbstract):
    ALLOWED_ALGORITHM = ['fixedStep']
    StartTime: float = 0.0
    BaseStepSize: float = None
    _algorithm: str = "fixedStep"
    Simulators: Union[List[OspSimulator], None] = None
    Functions: Union[OspFunctions, None] = None
    Connections: Union[OspConnections, None] = None
    version: str = "0.1"
    _required_keys = []

    def __init__(self, dict_xml: Dict = None, xml_source: str = None, **kwargs):
        """
        "StartTime", "BaseStepSize", "Algorithm", "Simulators", "Functions"
        "Connections", "version" arguments can be provided. Otherwise, a dictionary
        with the arguments as keys can be provided.

        Args:
            dict_xml(optional): Dictionary that contains the information of the system structure for the instance
            xml_source(optional): A string content of the XML file for the system structure or a path to the file
            StartTime(float, optional): Start time of the simulation. Default is 0.0 if not provided.
            BaseStepSize(float, optional): Global step size of the simulation. If not given, the smallest time step
                among the FMUs will be used.
            Simulators(List[OspSimulator], optional): Components for the system given as a list of OspSimulator
                instances
            Functions(List[OspFunctions], optional): Functions for the system given as a list of OspFunction
                instances
        """
        self.xs = xmlschema.XMLSchema(PATH_TO_XML_SCHEMA)
        if xml_source is not None:
            dict_xml = self.xs.to_dict(xml_source)
        super().__init__(dict_xml=dict_xml, **kwargs)

    # noinspection PyPep8Naming
    @property
    def Algorithm(self):
        return self._algorithm

    # noinspection PyPep8Naming
    @Algorithm.setter
    def Algorithm(self, value):
        if value in self.ALLOWED_ALGORITHM:
            self._algorithm = value
        else:
            raise ValueError('The algorithm for integration should be either of %s' % self.ALLOWED_ALGORITHM)

    def to_dict_xml(self):
        xs = xmlschema.XMLSchema(PATH_TO_XML_SCHEMA)
        dict_xml = {'@xmlns': xs.namespaces['osp']}
        if self.StartTime is not None:
            dict_xml['StartTime'] = self.StartTime
        if self.BaseStepSize is not None:
            dict_xml['BaseStepSize'] = self.BaseStepSize
        dict_xml['Algorithm'] = self._algorithm
        dict_xml['Simulators'] = {}
        if self.Simulators:
            dict_xml['Simulators']['Simulator'] = [
                simulator.to_dict_xml() for simulator in self.Simulators
            ]
        else:
            dict_xml['Simulators'] = None
        if self.Functions:
            dict_xml['Functions'] = self.Functions.to_dict_xml()
        if self.Connections:
            dict_xml['Connections'] = self.Connections.to_dict_xml()
        dict_xml['@version'] = self.version
        return dict_xml

    def from_dict_xml(self, dict_xml):
        direct_keys = ['StartTime', 'BaseStepSize', 'Algorithm']
        for key in direct_keys:
            if key in dict_xml:
                self.__setattr__(key, dict_xml[key])
        if 'Simulators' in dict_xml:
            if dict_xml['Simulators']:
                self.Simulators = []
                for simulator in dict_xml['Simulators']['Simulator']:
                    self.add_simulator(OspSimulator(dict_xml=simulator))
        if 'Functions' in dict_xml:
            if dict_xml['Functions']:
                self.Functions = OspFunctions(dict_xml=dict_xml['Functions'])
        if 'Connections' in dict_xml:
            if dict_xml['Connections']:
                self.Connections = OspConnections(dict_xml=dict_xml['Connections'])

    def add_simulator(self, simulator: OspSimulator):
        self.Simulators.append(simulator)

    def add_connection(
            self,
            connection: Union[
                OspVariableConnection,
                OspSignalConnection,
                OspVariableGroupConnection,
                OspSignalGroupConnection
            ]
    ):
        self.Connections.add_connection(connection)

    def to_xml_str(self):
        dict_xml = self.to_dict_xml()
        return xmlschema.etree_tostring(
            xmlschema.from_json(json.dumps(dict_xml), self.xs)
        )

    def from_xml(self, xml_source: str):
        self.from_dict_xml(self.xs.to_dict(xml_source))


OSP_VARIABLE_CLASS = {
    VariableType.Real: OspReal,
    VariableType.Integer: OspInteger,
    VariableType.String: OspString,
    VariableType.Boolean: OspBoolean
}
