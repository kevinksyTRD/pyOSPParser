"""System Configuration Module

This module contains all the classes to construct a class object to retrieve or deploy an xml file
of OSP System Structure for running OSP co-simulation. The OspSystemStructure class is one to use
to contain the data from the xml file or to create a xml from.

Example:
    A system structure can be built in a bottom-up way where an empty system structure is declared
    and component, function, connection, initial values are added afterward.

        from pyOSPParser.system_configuration import OspSystemStructure

        system = OspSystemStructure()
        system.add_component(OspSimulator(name='chassis', source='chassis.fmu'))
        system.add_component(OspSimulator(name='wheel', source='wheel.fmu'))
        system.add_connection(
            endpoint1=OspVariableEndpoint(simulator='chassis', name='shaft')
            endpoint2=OspVariableEndpoint(simulator='wheel', name='shaft')
            group=True
        )
        system.add_update_initial_value()
            component_name='chassis'
            init_value=OspInitialValue(variable='v0', value=OspReal(value=3.4))
        )

        xml_str = system.to_xml_str()

    If xml file is already available, you can create the system from the file.

        system = OspSystemStructure(xml_source=PATH_TO_XML_FILE)
"""

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
    """Enum used for variable type for initial values"""
    Real = 'Real'
    Integer = 'Integer'
    String = 'String'
    Boolean = 'Boolean'


class InterfaceType(Enum):
    """Interface type used for connections"""
    Variable = 'VariableConnection'
    Signal = 'SignalConnection'
    VariableGroup = 'VariableGroupConnection'
    SignalGroup = "SignalGroupConnection"


class FunctionType(Enum):
    """Function type used for functions"""
    LinearTransformation = 1
    Sum = 2
    VectorSum = 3


class OspSystemStructureAbstract(ABC):
    """Abstract class for most of classes in this module"""
    @property
    @abstractmethod
    def _required_keys(self):
        pass

    def __init__(self, dict_xml: Union[Dict, None] = None, **kwargs):
        """Construnctor for the base class

        This constructor assigns the attribute of the instance from the dictionary
        that contains the required keys or from the required arguments given. If
        neither required arguments nor the dictionary are not given, it will cause
        an TypeError.
        """
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
        pass

    @abstractmethod
    def from_dict_xml(self, dict_xml: Dict):
        pass


class Value(OspSystemStructureAbstract):
    """Base class for value classes for initial values"""
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
    _required_keys = ['value']

    def __init__(self, dict_xml: Dict = None, **kwargs):
        """Contructor for OspInteger

        One should provide either 'dict_xml(dictionary)' that has a key of
        '@value') or 'value' (integer) as a argument.

        Args:
            dict_xml(optional) {'@value': bool}
            value(integer, optional): actual value
        """
        super().__init__(dict_xml=dict_xml, **kwargs)
        value = kwargs.get('value', None)
        if value is not None:
            if not isinstance(value, int):
                if isinstance(value, float):
                    self.value = int(value)
                else:
                    raise TypeError('The value should be of integer type.')


class OspBoolean(Value):
    """
    The "name" member is used in other application. Please make sure that
    the value is not changed without cross-checking
    """
    value: bool
    name = 'Boolean'
    _required_keys = ['value']

    def __init__(self, dict_xml: Dict = None, **kwargs):
        """Contructor for OspBoolean

        One should provide either 'dict_xml(dictionary)' that has a key of
        '@value') or 'value' (bool) as a argument.

        Args:
            dict_xml(optional) {'@value': bool}
            value(bool, optional): actual value
        """
        super().__init__(dict_xml=dict_xml, **kwargs)
        value = kwargs.get('value', None)
        if value is not None:
            if not isinstance(value, bool):
                raise TypeError('The value should be of boolean type.')


class OspString(Value):
    """
    The "name" member is used in other application. Please make sure that
    the value is not changed without cross-checking
    """
    value: str
    name = 'String'
    _required_keys = ['value']

    def __init__(self, dict_xml: Dict = None, **kwargs):
        """Contructor for OspString

        One should provide either 'dict_xml(dictionary)' that has a key of
        '@value') or 'value' (string) as a argument.

        Args:
            dict_xml {'@value': string}
        """
        super().__init__(dict_xml=dict_xml, **kwargs)
        value = kwargs.get('value', None)
        if value is not None:
            if not isinstance(value, str):
                raise TypeError('The value should be of string type.')


class OspReal(Value):
    """
    The "name" member is used in other application. Please make sure that
    the value is not changed without cross-checking. One should provide 'value' argument
    with initilaization.
    """
    value: float
    name = 'Real'
    _required_keys = ['value']

    def __init__(self, dict_xml=None, **kwargs):
        """Contructor for OspReal

        One should provide either 'dict_xml(dictionary)' that has a key of
        '@value') or 'value' (float) as a argument.

        Args:
            dict_xml(optional) {'@value': float}
            value(float, optional) Actual value
        """
        super().__init__(dict_xml=dict_xml, **kwargs)
        value = kwargs.get('value', None)
        if value is not None:
            if not isinstance(value, float):
                if isinstance(value, int):
                    self.value = float(value)
                else:
                    raise TypeError('The value should be of float type.')
            


class OspInitialValue(OspSystemStructureAbstract):
    variable: str
    value: Union[OspReal, OspInteger, OspBoolean, OspString]
    _required_keys = ['variable', 'value']

    def __init__(self, dict_xml=None, **kwargs):
        """
        Constructor for OspInitialValue.

        One should provide either 'dict_xml(dictionary)' that has a key of
        'variable' and 'value) or 'variable (str)' and
        'value (OspReal, OspInteger, OspString, OspBoolean)' as arguments.

        Args:
            variable 
            value
            dict_xml

        Exceptions:
            TypeError if the required arguments are not given
                (either dict_xml or variable and value)
            TypeError if you provide a wrong type for the value argument. It should be either
                OspReal, OspInteger, OspString or OspBoolean

        """
        super().__init__(dict_xml=dict_xml, **kwargs)
        if kwargs.get('value', None) is not None:
            if type(kwargs.get('value', None)) not in [OspReal, OspInteger, OspString, OspBoolean]:
                raise TypeError('The value should be of either OspReal, '
                                'OspInteger, OspString or OspBoolean type')

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

    def __init__(self, dict_xml: Dict = None, **kwargs):
        """Construction method for OspSimulator. 'name' and 'source' are required arguments.
        Otherwise, 'dict_xml' that has the arguments as a dictionary can be provided.
        """
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
            self.source = dict_xml['@source'][idx + 1:]
            self.fmu_rel_path = dict_xml['@source'][:idx + 1]
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
        "VariableGroup" and "SignalGroup" arguments are required. Otherwise, one can
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
            ] = None,
            source: Union[OspVariableEndpoint, OspSignalEndpoint] = None,
            target: Union[OspVariableEndpoint, OspSignalEndpoint] = None,
            group: bool = None,
    ) -> Union[
        OspVariableConnection,
        OspSignalConnection,
        OspVariableGroupConnection,
        OspSignalGroupConnection
    ]:
        """Add a connection from the given connection directly or from a source, target and whether
        the connection is group

        Args:
            connection
            source
            target
            group

        Returns:
            An OspVariableConnection or others created

        Exceptions:
            TypeError if the connection provided is not of proper type, when missing one of
            source, target and group arguments, or when both endpoints are of signal type.
        """
        if connection is not None:
            if type(connection) is OspVariableConnection:
                if self.VariableConnection:
                    self.VariableConnection.append(connection)
                else:
                    self.VariableConnection = [connection]
            elif type(connection) is OspSignalConnection:
                if self.SignalConnection:
                    self.SignalConnection.append(connection)
                else:
                    self.SignalConnection = [connection]
            elif type(connection) is OspVariableGroupConnection:
                if self.VariableGroupConnection:
                    self.VariableGroupConnection.append(connection)
                else:
                    self.VariableGroupConnection = [connection]
            elif type(connection) is OspSignalGroupConnection:
                if self.SignalGroupConnection:
                    self.SignalGroupConnection.append(connection)
                else:
                    self.SignalGroupConnection = [connection]
            else:
                msg = 'The type of the connections should be either "OspVariableConnection", ' \
                      '"OspSignalConnection", "OspVariableGroupConnection" or ' \
                      '"OspSignalGroupConnection"'
                raise TypeError(msg)
        else:
            if source is None or target is None or group is None:
                raise TypeError('You must provide a source, a target and '
                                'whether it is a group connection.')
            if group:
                if type(source) is OspSignalEndpoint or type(target) is OspSignalEndpoint:
                    # SignalGroupConnection
                    if type(source) is OspSignalEndpoint and type(target) is OspVariableEndpoint:
                        connection = OspSignalGroupConnection(
                            VariableGroup=target, SignalGroup=source
                        )
                    elif type(target) is OspSignalEndpoint and type(source) is OspVariableEndpoint:
                        connection = OspSignalGroupConnection(
                            VariableGroup=source, SignalGroup=target
                        )
                    else:
                        raise TypeError('The endpoint cannot be both of signal type.')
                    if self.SignalGroupConnection:
                        self.SignalGroupConnection.append(connection)
                    else:
                        self.SignalGroupConnection = [connection]
                else:
                    # VariableGroupConnection
                    connection = OspVariableGroupConnection(VariableGroup=[source, target])
                    if self.VariableGroupConnection:
                        self.VariableGroupConnection.append(connection)
                    else:
                        self.VariableGroupConnection = [connection]
            else:
                if type(source) is OspSignalEndpoint or type(target) is OspSignalEndpoint:
                    # SignalConnection
                    if type(source) is OspSignalEndpoint and type(target) is OspVariableEndpoint:
                        connection = OspSignalConnection(
                            Variable=target, Signal=source
                        )
                    elif type(target) is OspSignalEndpoint and type(source) is OspVariableEndpoint:
                        connection = OspSignalConnection(
                            Variable=source, Signal=target
                        )
                    else:
                        raise TypeError('The endpoint cannot be both of signal type.')
                    if self.SignalConnection:
                        self.SignalConnection.append(connection)
                    else:
                        self.SignalConnection = [connection]
                else:
                    # VariableConnection
                    connection = OspVariableConnection(Variable=[source, target])
                    if self.VariableConnection:
                        self.VariableConnection.append(connection)
                    else:
                        self.VariableConnection = [connection]
        return connection

    def find_and_delete_connection(
            self,
            endpoint1: Union[OspVariableEndpoint, OspSignalEndpoint],
            endpoint2: Union[OspVariableEndpoint, OspSignalEndpoint],
            connections: Union[
                List[OspVariableConnection],
                List[OspVariableGroupConnection],
                List[OspSignalConnection],
                List[OspSignalGroupConnection]
            ]
    ) -> Union[
        OspVariableConnection,
        OspVariableGroupConnection,
        OspSignalConnection,
        OspSignalGroupConnection,
        bool
    ]:
        if type(connections[0]) is OspSignalConnection or \
                type(connections[0]) is OspSignalGroupConnection:
            if type(endpoint1) is OspSignalEndpoint:
                sig_endpoint = endpoint1
                var_endpoint = endpoint2
            else:
                sig_endpoint = endpoint2
                var_endpoint = endpoint1
            connection = self.find_connection_for_signal_or_signal_groups(
                sig_endpoint=sig_endpoint,
                var_endpoint=var_endpoint,
                connections=connections
            )
        else:
            connection = self.find_connection_for_variables_or_variable_groups(
                endpoint1=endpoint1,
                endpoint2=endpoint2,
                connections=connections
            )
        if connection:
            return connections.pop(
                connections.index(connection)
            )
        else:
            return False

    def delete_connection(
            self,
            endpoint1: Union[OspVariableEndpoint, OspSignalEndpoint],
            endpoint2: Union[OspVariableEndpoint, OspSignalEndpoint],
    ) -> Union[
        OspVariableConnection,
        OspVariableGroupConnection,
        OspSignalConnection,
        OspSignalGroupConnection,
        bool,
    ]:
        """
        Delete a connection found from the source and target endpoints.

        Returns:
            bool, True if found and deleted. False, otherwise.

        Exceptions:
            TypeError if there is no connection with the corresponding type of endpoints.
        """
        error_msg = 'There is no connection to delete for this type of endpoint'
        deleted_connection = False
        # noinspection DuplicatedCode
        if type(endpoint1) is OspSignalEndpoint or type(endpoint2) is OspSignalEndpoint:
            # The connection is either OspSignalGroupConnection or OspSignalConnection
            if self.SignalConnection is None and self.SignalGroupConnection is None:
                raise TypeError(error_msg)
            if self.SignalConnection:
                deleted_connection = self.find_and_delete_connection(
                    endpoint1=endpoint1,
                    endpoint2=endpoint2,
                    connections=self.SignalConnection
                )
                if len(self.SignalConnection) == 0:
                    self.SignalConnection = None

            if not deleted_connection and self.SignalGroupConnection:
                deleted_connection = self.find_and_delete_connection(
                    endpoint1=endpoint1,
                    endpoint2=endpoint2,
                    connections=self.SignalGroupConnection
                )
                if len(self.SignalGroupConnection) == 0:
                    self.SignalGroupConnection = None

            return deleted_connection

        else:
            # The connection is either OspVariableGroupConnection or OspVariableConnection
            if self.VariableConnection is None and self.VariableGroupConnection is None:
                raise TypeError(error_msg)
            if self.VariableConnection:
                deleted_connection = self.find_and_delete_connection(
                    endpoint1=endpoint1,
                    endpoint2=endpoint2,
                    connections=self.VariableConnection
                )
                if len(self.VariableConnection) == 0:
                    self.VariableConnection = None

            if not deleted_connection and self.VariableGroupConnection:
                deleted_connection = self.find_and_delete_connection(
                    endpoint1=endpoint1,
                    endpoint2=endpoint2,
                    connections=self.VariableGroupConnection
                )
                if len(self.VariableGroupConnection) == 0:
                    self.VariableGroupConnection = None

            return deleted_connection

    @staticmethod
    def find_connection_for_variables_or_variable_groups(
            endpoint1: OspVariableEndpoint,
            endpoint2: OspVariableEndpoint,
            connections: [
                List[OspVariableConnection],
                List[OspVariableGroupConnection],
            ]
    ) -> Union[OspVariableConnection, OspVariableGroupConnection, bool]:
        """Find a connection from source and target endpoints for variable / variable
        group connection. Returns False if not found"""
        if type(connections[0]) is OspVariableConnection:
            var_type = 'Variable'
        elif type(connections[0]) is OspVariableGroupConnection:
            var_type = 'VariableGroup'
        else:
            raise TypeError('connections should be a list of OspVariableConnection '
                            'or OspVariableGroupConnection')
        for connection in connections:
            components = [variable.simulator for variable in getattr(connection, var_type)]
            variables = [variable.name for variable in getattr(connection, var_type)]
            if endpoint1.simulator in components and \
                    endpoint1.name in variables and \
                    endpoint2.simulator in components and \
                    endpoint1.name in variables:
                return connection
        return False

    @staticmethod
    def find_connection_for_signal_or_signal_groups(
            sig_endpoint: OspSignalEndpoint,
            var_endpoint: OspVariableEndpoint,
            connections: [
                List[OspSignalConnection],
                List[OspSignalGroupConnection],
            ]
    ) -> Union[OspSignalConnection, OspSignalGroupConnection, bool]:
        """Find a connection from source and target endpoints for signal / signal
        group connection. Returns False if not found"""
        if type(connections[0]) is OspSignalConnection:
            sig_type = 'Signal'
            var_type = 'Variable'
        elif type(connections[0]) is OspSignalGroupConnection:
            var_type = 'VariableGroup'
            sig_type = 'SignalGroup'
        else:
            raise TypeError('connections should be a list of OspSignalConnection or '
                            'OspSignalGroupConnection')
        for connection in connections:
            component = getattr(connection, var_type).simulator
            function = getattr(connection, sig_type).function
            variable = getattr(connection, var_type).name
            func_variable = getattr(connection, sig_type).name
            if sig_endpoint.function == function and \
                    sig_endpoint.name == func_variable and \
                    var_endpoint.simulator == component and \
                    var_endpoint.name == variable:
                return connection
        return False


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

    def get_function_names(self) -> Union[List[str], None]:
        """Return a list of function names or None if not found."""
        names = []
        if self.LinearTransformation:
            names.extend([function.name for function in self.LinearTransformation])
        if self.Sum:
            names.extend([function.name for function in self.Sum])
        if self.VectorSum:
            names.extend([function.name for function in self.VectorSum])
        if len(names) == 0:
            return None
        else:
            return names

    # noinspection PyIncorrectDocstring
    def add_function(self, name: str, function_type: FunctionType, **kwargs):
        """Add a function

        'factor', 'offset' arguments are required for FunctionType.LinearTransformation
        'inputCount' is required for FunctionType.Sum
        'inputCount', 'dimension' are required for FunctionType.VectorSumFunction

        Args:
            name: Name of the function
            function_type: Either of FunctionType.LinearTransformation, FunctionType.Sum or
                FunctionType.VectorSum
            factor (float): factor for linear transformation f(x) = factor * x + offset
            offset (float): offset for linear transformation f(x) = factor * x + offset
            inputCount (int): number of inputs for sum or vector sum
            dimension (int): Dimension of a vector for vector sum

        Returns:
            OspLinearTransformationFunction, OspSumFunction, OspVectorSumFunction

        Exceptions:
            TypeError if correct arguments are not given for a function type or function name is
            duplicate
        """
        # Check if the function name is not duplicate
        function_names = self.get_function_names()
        if function_names is not None:
            if name in function_names:
                raise TypeError('The function name already exists.')

        if function_type == FunctionType.LinearTransformation:
            factor = kwargs.get('factor', None)
            if factor is None:
                raise TypeError('"factor" argument is missing for linear transformation function')
            offset = kwargs.get('offset', None)
            if offset is None:
                raise TypeError('"offset" argument is missing for linear transformation function')
            function = OspLinearTransformationFunction(
                name=name, factor=factor, offset=offset
            )
            if self.LinearTransformation:
                self.LinearTransformation.append(function)
            else:
                self.LinearTransformation = [function]
            return function

        if function_type == FunctionType.Sum:
            input_count = kwargs.get('inputCount', None)
            if input_count is None:
                raise TypeError('"inputCount" argument is missing for sum function')
            function = OspSumFunction(name=name, inputCount=input_count)
            if self.Sum:
                self.Sum.append(function)
            else:
                self.Sum = [function]
            return function

        if function_type == FunctionType.VectorSum:
            input_count = kwargs.get('inputCount', None)
            if input_count is None:
                raise TypeError('"inputCount" argument is missing for vector sum function')
            dimension = kwargs.get('dimension', None)
            if dimension is None:
                raise TypeError('"dimension" argument is missing for vector sum function')
            function = OspVectorSumFunction(name=name, inputCount=input_count, dimension=dimension)
            if self.VectorSum:
                self.VectorSum.append(function)
            else:
                self.VectorSum = [function]
            return function

    @staticmethod
    def find_function(name: str, functions: List[Union[
        OspLinearTransformationFunction,
        OspSumFunction,
        OspVectorSumFunction
    ]]) -> Union[
        OspLinearTransformationFunction,
        OspSumFunction,
        OspVectorSumFunction,
        bool
    ]:
        """Find a function

        Returns:
            OspLinearTransformationFunction, OspSumFunction, OspVectorSumFunction, bool:
            deleted function. False if the function is not found.

        Exceptions:
            StopIteration if the function is not found.
        """
        try:
            return next(function for function in functions if function.name == name)
        except StopIteration:
            return False

    def delete_function(self, name: str) -> Union[
        OspLinearTransformationFunction,
        OspSumFunction,
        OspVectorSumFunction,
        bool
    ]:
        """Delete a function

        Returns:
            OspLinearTransformationFunction, OspSumFunction, OspVectorSumFunction, bool:
            deleted function. False if the function is not found.
        """
        if self.LinearTransformation:
            function = self.find_function(name, self.LinearTransformation)
            if function:
                deleted_function = self.LinearTransformation.pop(
                    self.LinearTransformation.index(function)
                )
                if len(self.LinearTransformation) == 0:
                    self.LinearTransformation = None
                return deleted_function
        if self.Sum:
            function = self.find_function(name, self.Sum)
            if function:
                deleted_function = self.Sum.pop(self.Sum.index(function))
                if len(self.Sum) == 0:
                    self.Sum = None
                return deleted_function
        if self.VectorSum:
            function = self.find_function(name, self.VectorSum)
            if function:
                deleted_function = self.VectorSum.pop(self.VectorSum.index(function))
                if len(self.VectorSum) == 0:
                    self.VectorSum = None
                return deleted_function
        return False


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
            dict_xml(optional): Dictionary that contains the information of the system structure
                for the instance
            xml_source(optional): A string content of the XML file for the system structure or a
                path to the file
            StartTime(float, optional): Start time of the simulation.
                Default is 0.0 if not provided.
            BaseStepSize(float, optional): Global step size of the simulation.
                If not given, the smallest time step among the FMUs will be used.
            Simulators(List[OspSimulator], optional): Components for the system given
                as a list of OspSimulator instances
            Functions(List[OspFunctions], optional): Functions for the system given
                as a list of OspFunction instances
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
            raise ValueError(
                'The algorithm for integration should be either of %s' % self.ALLOWED_ALGORITHM)

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
        if self.Simulators:
            if simulator.name in [Simulator.name for Simulator in self.Simulators]:
                raise TypeError('The name of the simulator already exists.')
            self.Simulators.append(simulator)
        else:
            self.Simulators = [simulator]

    def delete_simulator(self, name: str) -> OspSimulator:
        """Delete a simulator

        Args:
            name: Name of the component to be deleted

        Returns:
            a simulator(component) deleted.
        """
        if self.Simulators:
            try:
                component = next(
                    comp for comp in self.Simulators if comp.name == name
                )
            except StopIteration:
                raise TypeError(f'No component if found with the name, {name}')
            return self.Simulators.pop(self.Simulators.index(component))
        else:
            raise TypeError('There is no component to delete')

    def get_all_endpoints_for_component(self, component_name: str) -> List[OspVariableEndpoint]:
        if self.Connections:
            return [
                endpoint for connection in self.Connections.VariableConnection
                for endpoint in connection.Variable if endpoint.simulator == component_name
            ]
        else:
            raise TypeError('There is no connection in the system.')

    def validate_connection(
            self,
            connection: Union[
                OspVariableConnection,
                OspSignalConnection,
                OspVariableGroupConnection,
                OspSignalGroupConnection
            ] = None,
            source: Union[OspVariableEndpoint, OspSignalEndpoint] = None,
            target: Union[OspVariableEndpoint, OspSignalEndpoint] = None
    ):
        """Validates connection. Checks if the connection refers to the components in the system

        Exceptions:
            AssertionError if a component or function is not found in the system
            TypeError if source or target is missing when connection is not given.
        """
        no_comp_err_msg = 'There is no component to connect in the system'
        no_func_err_msg = 'There is no function to connect in the system'
        comp_not_found_err_msg = 'No component is found with the name: '
        func_not_found_err_msg = 'No function is found with the name: '
        assert self.Simulators, no_comp_err_msg
        component_names = [Simulator.name for Simulator in self.Simulators]
        function_names = [Function for Function in self.Functions.get_function_names()] \
            if self.Functions else []
        if connection:
            if type(connection) is OspVariableConnection:
                for endpoint in connection.Variable:
                    assert endpoint.simulator in component_names, \
                        f'{comp_not_found_err_msg} {endpoint.simulator}'
            elif type(connection) is OspVariableGroupConnection:
                for endpoint in connection.VariableGroup:
                    assert endpoint.simulator in component_names, \
                        f'{comp_not_found_err_msg} {endpoint.simulator}'
            elif type(connection) is OspSignalConnection:
                assert self.Functions, no_func_err_msg
                assert connection.Signal.function in function_names, \
                    f'{func_not_found_err_msg} {connection.Signal.function}'
                assert connection.Variable.simulator in component_names, \
                    f'{comp_not_found_err_msg} {connection.Variable.simulator}'
            elif type(connection) is OspSignalGroupConnection:
                assert self.Functions, no_func_err_msg
                assert connection.SignalGroup.function in function_names, \
                    f'{func_not_found_err_msg} {connection.SignalGroup.function}'
                assert connection.VariableGroup.simulator in component_names, \
                    f'{comp_not_found_err_msg} {connection.VariableGroup.simulator}'
        else:
            if source is None or target is None:
                raise TypeError('Both source and target should be provided.')
            if type(source) is OspSignalEndpoint:
                assert self.Functions, no_func_err_msg
                assert source.function in function_names, \
                    f'{func_not_found_err_msg} {source.function}'
            else:
                assert source.simulator in component_names, \
                    f'{comp_not_found_err_msg} {source.simulator}'
            if type(target) is OspSignalEndpoint:
                assert self.Functions, no_func_err_msg
                assert target.function in function_names, \
                    f'{func_not_found_err_msg} {target.function}'
            else:
                assert target.simulator in component_names, \
                    f'{comp_not_found_err_msg} {target.simulator}'

    def add_connection(
            self,
            connection: Union[
                OspVariableConnection,
                OspSignalConnection,
                OspVariableGroupConnection,
                OspSignalGroupConnection
            ] = None,
            source: Union[OspVariableEndpoint, OspSignalEndpoint] = None,
            target: Union[OspVariableEndpoint, OspSignalEndpoint] = None,
            group: bool = None
    ) -> Union[
        OspVariableConnection,
        OspSignalConnection,
        OspVariableGroupConnection,
        OspSignalGroupConnection
    ]:
        """Adds a connection

        You should provide either connection instance directly or provide source, target and whether
        the connection is group together.

        Returns:
             connections added
        """
        connection_was_none = self.Connections is None
        if self.Connections is None:
            self.Connections = OspConnections()
        try:
            if connection:
                self.validate_connection(connection=connection)
                return self.Connections.add_connection(connection=connection)
            else:
                self.validate_connection(source=source, target=target)
                return self.Connections.add_connection(source=source, target=target, group=group)
        except TypeError as e:
            if connection_was_none:
                self.Connections = None
            raise TypeError(e.__str__())

    def delete_connection(
            self,
            endpoint1: Union[OspVariableEndpoint, OspSignalEndpoint],
            endpoint2: Union[OspVariableEndpoint, OspSignalEndpoint]
    ) -> Union[
        OspVariableConnection,
        OspSignalConnection,
        OspVariableGroupConnection,
        OspSignalGroupConnection
    ]:
        """Delete a variable connection. Don't use it to delete a variable

        Returns:
            OspVariableConnection, OspSignalConnection, OspVariableGroupConnection,
            OspSignalGroupConnection, bool: deleted connection or False if the connection is not
            found.

        Exceptions:
            TypeError: No connection to delete
        """
        if self.Connections:
            connection_deleted = self.Connections.delete_connection(endpoint1, endpoint2)
            if self.Connections.VariableConnection is None and \
                    self.Connections.VariableGroupConnection is None and \
                    self.Connections.SignalConnection is None and \
                    self.Connections.SignalGroupConnection is None:
                self.Connections = None
            return connection_deleted
        else:
            raise TypeError('There is no connection to delete')

    def add_update_initial_value(
            self,
            component_name: str,
            init_value: OspInitialValue
    ) -> bool:
        """Add or update an initial value to a component"""

        component = self.get_component_by_name(component_name)
        # Search for an initial value among those already exist and update it
        if component.InitialValues:
            try:
                init_value_to_update = next(
                    value for value in component.InitialValues
                    if value.variable == init_value.variable
                )
                init_value_to_update.value = init_value.value
            except StopIteration:
                # Create a new initial value otherwise.
                component.InitialValues.append(init_value)
        else:
            component.InitialValues = [init_value]

        return True

    def delete_initial_value(self, component_name: str, variable: str) -> bool:
        """Delete an initial value"""
        component = self.get_component_by_name(component_name)
        try:
            index = next(
                i for i, value in enumerate(component.InitialValues) if value.variable == variable
            )
            component.InitialValues.pop(index)
            if len(component.InitialValues) == 0:
                component.InitialValues = None
        except StopAsyncIteration:
            raise TypeError(f'No initial value is found for the variable given: {variable}')
        return True

    def get_component_by_name(self, name: str) -> OspSimulator:
        """Returns a component if it is found with the name given. Unless, a TypeError is raised."""
        try:
            return next(
                component for component in self.Simulators if component.name == name
            )
        except StopIteration:
            raise TypeError('The component is not found with the given name.')

    # noinspection PyIncorrectDocstring
    def add_function(self, function_name: str, function_type: FunctionType, **kwargs) \
            -> Union[OspLinearTransformationFunction, OspSumFunction, OspVectorSumFunction]:
        """Add a function

        'factor', 'offset' arguments are required for FunctionType.LinearTransformation
        'inputCount' is required for FunctionType.Sum
        'inputCount', 'dimension' are required for FunctionType.VectorSumFunction

        Args:
            function_name: Name of the function
            function_type: Either of FunctionType.LinearTransformation, FunctionType.Sum or
                FunctionType.VectorSum
            factor (float): factor for linear transformation f(x) = factor * x + offset
            offset (float): offset for linear transformation f(x) = factor * x + offset
            inputCount (int): number of inputs for sum or vector sum
            dimension (int): Dimension of a vector for vector sum

        Returns:
            OspLinearTransformationFunction, OspSumFunction, OspVectorSumFunction

        Exceptions:
            TypeError if correct arguments are not given for a function type
        """
        function_was_none = self.Functions is None
        if function_was_none:
            self.Functions = OspFunctions()
        try:
            return self.Functions.add_function(
                name=function_name, function_type=function_type, **kwargs
            )
        except TypeError as e:
            if function_was_none:
                self.Functions = None
            raise TypeError(e.__str__())

    def delete_function(self, function_name: str):
        """Delete a function

        Returns:
            OspLinearTransformationFunction, OspSumFunction, OspVectorSumFunction, bool:
            deleted function. False if the function is not found.
        """
        if self.Functions is None:
            raise TypeError('There is no function.')
        deleted_function = self.Functions.delete_function(
            name=function_name
        )
        if self.Functions.LinearTransformation is None and \
                self.Functions.VectorSum is None and \
                self.Functions.Sum is None:
            self.Functions = None
        return deleted_function

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
