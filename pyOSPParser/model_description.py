import json
import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import NamedTuple, Union, List, Dict

import xmlschema

PATH_TO_XML_SCHEMA = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'xmlschema',
    'OspModelDescription.xsd'
)


class InterfaceError(Exception):
    pass


class Causality(Enum):
    input = 0
    output = 1
    no_variable = 2


class InterfaceIndex(NamedTuple):
    type_name: str
    index: int


class OspModelDescriptionAbstract(ABC):
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


class OspBaseUnit(OspModelDescriptionAbstract):
    kg: int = 0
    m: int = 0
    s: int = 0
    A: int = 0
    K: int = 0
    mol: int = 0
    cd: int = 0
    rad: int = 0
    factor: float = 1
    offset: float = 0
    _required_keys = []

    def __init__(self, dict_xml: Dict = None, **kwargs):
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        return {
            '@kg': self.kg, '@m': self.m, '@s': self.s, '@A': self.A,
            '@K': self.K, '@mol': self.mol, '@cd': self.cd, '@rad': self.rad,
            '@factor': self.factor, '@offset': self.offset
        }

    def to_dict(self):
        return {
            'kg': self.kg, 'm': self.m, 's': self.s, 'A': self.A,
            'K': self.K, 'mol': self.mol, 'cd': self.cd, 'rad': self.rad,
            'factor': self.factor, 'offset': self.offset
        }

    def from_dict_xml(self, dict_xml: Dict):
        self.kg = dict_xml.get('@kg', 0)
        self.m = dict_xml.get('@m', 0)
        self.s = dict_xml.get('@s', 0)
        self.A = dict_xml.get('@A', 0)
        self.K = dict_xml.get('@K', 0)
        self.mol = dict_xml.get('@mol', 0)
        self.cd = dict_xml.get('@cd', 0)
        self.rad = dict_xml.get('@rad', 0)
        self.factor = dict_xml.get('@factor', 0)
        self.offset = dict_xml.get('@offset', 0)


class OspDisplayUnit(OspModelDescriptionAbstract):
    name: str
    factor: float = 1
    offset: float = 1
    _required_keys = ['name', 'factor', 'offset']

    def __init__(self, dict_xml: Union[Dict, None] = None, **kwargs):
        """Constructor for OspDisplayUnit class

        Args:
            dict_xml(Dict, Optional): Dictionaly that contains the information of the instance
            name(str): Name of the unit
            factor(float): Factor of the unit
            offset(offset): Offset of the unit
        """
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        return {
            '@name': self.name, '@factor': self.factor, '@offset': self.offset
        }

    def to_dict(self):
        return {
            'name': self.name, 'factor': self.factor, 'offset': self.offset
        }

    def from_dict_xml(self, dict_xml: Dict):
        self.name = dict_xml['@name']
        self.factor = dict_xml['@factor']
        self.offset = dict_xml['@offset']


class Ospfmi2Unit(OspModelDescriptionAbstract):
    name: str = None
    BaseUnit: OspBaseUnit = None
    DisplayUnit: List[OspDisplayUnit] = None
    _required_keys = ['name', 'BaseUnit', 'DisplayUnit']

    def __init__(self, dict_xml: Dict = None, **kwargs):
        """Constructor for the Ospfmu2Unit class

        Args:
            dict_xml(dict): Dictionary that contains the information of the instance
            name(str): Name of the unit
            BaseUnit: BaseUnit instance
            DisplayUnit: List of DisplayUnit instances

        """
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        dict_xml = {
            '@name': self.name,
            'BaseUnit': self.BaseUnit.to_dict_xml(),
        }
        if self.DisplayUnit is not None:
            dict_xml['DisplayUnit'] = [unit.to_dict_xml() for unit in self.DisplayUnit]
        return dict_xml

    def to_dict(self):
        return {
            'BaseUnit': self.BaseUnit.to_dict(),
            'DisplayUnit': None if self.DisplayUnit is None
            else [unit.to_dict() for unit in self.DisplayUnit],
            'name': self.name
        }

    def from_dict_xml(self, dict_xml: Dict):
        self.name = dict_xml['@name']
        self.BaseUnit = OspBaseUnit(dict_xml=dict_xml['BaseUnit'])
        self.DisplayUnit = None if 'DisplayUnit' not in dict_xml else \
            [OspDisplayUnit(dict_xml=du) for du in dict_xml['DisplayUnit']]


class OspUnitType(Ospfmi2Unit):
    pass


class OspUnitDefinitionsType(OspModelDescriptionAbstract):
    Unit: Union[List[OspUnitType], None] = None
    _required_keys = []

    def __init__(self, dict_xml: Dict = None, **kwargs):
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        return {
            'Unit': None if self.Unit is None else [unit.to_dict_xml() for unit in self.Unit]
        }

    def to_dict(self):
        return {
            'Unit': None if self.Unit is None else [unit.to_dict() for unit in self.Unit]
        }

    def from_dict_xml(self, dict_xml: Dict):
        self.Unit = [OspUnitType(dict_xml=ut) for ut in dict_xml.get('Unit', [])]
        if len(self.Unit) == 0:
            self.Unit = None

    def add_unit_type(self, unit_type: OspUnitType):
        self.Unit.append(unit_type)


class OspVariableType(OspModelDescriptionAbstract):
    ref: str = None
    unit: str = None
    _required_keys = ['ref']

    def __init__(self, dict_xml: Dict = None, **kwargs):
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        dict_xml = {'@ref': self.ref}
        if self.unit:
            dict_xml['@unit'] = self.unit
        return dict_xml

    def to_dict(self):
        return {
            'ref': self.ref,
            'unit': self.unit
        }

    def from_dict_xml(self, dict_xml: Dict):
        self.ref = dict_xml['@ref']
        self.unit = dict_xml.get('@unit', None)


class OspPhysicalTypeBase(OspModelDescriptionAbstract):
    name: str = None
    Variable: List[OspVariableType] = None
    _required_keys = ['name', 'Variable']

    def __init__(self, dict_xml: Dict = None, **kwargs):
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        return {
            '@name': self.name,
            'Variable': [variable.to_dict_xml() for variable in self.Variable],
        }

    def to_dict(self):
        return {
            'Variable': [variable.to_dict() for variable in self.Variable],
            'name': self.name
        }

    def from_dict_xml(self, dict_xml):
        self.name = dict_xml['@name']
        self.Variable = [
            OspVariableType(dict_xml=variable) for variable in dict_xml.get('Variable', [])
        ]


class OspForceType(OspPhysicalTypeBase):
    pass


class OspTorqueType(OspPhysicalTypeBase):
    pass


class OspVoltageType(OspPhysicalTypeBase):
    pass


class OspPressureType(OspPhysicalTypeBase):
    pass


class OspLinearVelocityType(OspPhysicalTypeBase):
    pass


class OspAngularVelocityType(OspPhysicalTypeBase):
    pass


class OspCurrentType(OspPhysicalTypeBase):
    pass


class OspVolumeFlowRateType(OspPhysicalTypeBase):
    pass


class OspLinearDisplacementType(OspPhysicalTypeBase):
    pass


class OspAngularDisplacementType(OspPhysicalTypeBase):
    pass


class OspChargeType(OspPhysicalTypeBase):
    pass


class OspVolumeType(OspPhysicalTypeBase):
    pass


class OspLinearMechanicalPortType(OspModelDescriptionAbstract):
    Force: OspForceType
    LinearVelocity: OspLinearVelocityType
    name: str
    _required_keys = ['name', 'LinearVelocity', 'Force']

    def __init__(self, dict_xml: Dict = None, **kwargs):
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        return {
            '@name': self.name,
            'Force': self.Force.to_dict_xml(),
            'LinearVelocity': self.LinearVelocity.to_dict_xml()
        }

    def to_dict(self):
        return {
            'Force': self.Force.to_dict(),
            'LinearVelocity': self.LinearVelocity.to_dict(),
            'name': self.name
        }

    def from_dict_xml(self, dict_xml: Dict):
        self.name = dict_xml['@name']
        self.Force = OspForceType(dict_xml=dict_xml['Force'])
        self.LinearVelocity = OspLinearVelocityType(dict_xml=dict_xml['LinearVelocity'])


class OspAngularMechanicalPortType(OspModelDescriptionAbstract):
    Torque: OspTorqueType
    AngularVelocity: OspAngularVelocityType
    name: str
    _required_keys = ['name', 'Torque', 'AngularVelocity']

    def __init__(self, dict_xml: Dict = None, **kwargs):
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        return {
            '@name': self.name,
            'Torque': self.Torque.to_dict_xml(),
            'AngularVelocity': self.AngularVelocity.to_dict_xml(),
        }

    def to_dict(self):
        return {
            'Torque': self.Torque.to_dict(),
            'AngularVelocity': self.AngularVelocity.to_dict(),
            'name': self.name
        }

    def from_dict_xml(self, dict_xml: Dict):
        self.name = dict_xml['@name']
        self.Torque = OspTorqueType(dict_xml=dict_xml['Torque'])
        self.AngularVelocity = OspAngularVelocityType(dict_xml=dict_xml['AngularVelocity'])


class OspElectromagneticPortType(OspModelDescriptionAbstract):
    Voltage: OspVoltageType
    Current: OspCurrentType
    name: str
    _required_keys = ['name', 'Voltage', 'Current']

    def __init__(self, dict_xml: Dict = None, **kwargs):
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        return {
            '@name': self.name,
            'Voltage': self.Voltage.to_dict_xml(),
            'Current': self.Current.to_dict_xml(),
        }

    def to_dict(self):
        return {
            'Voltage': self.Voltage.to_dict(),
            'Current': self.Current.to_dict(),
            'name': self.name
        }

    def from_dict_xml(self, dict_xml: Dict):
        self.name = dict_xml['@name']
        self.Voltage = OspVoltageType(dict_xml=dict_xml['Voltage'])
        self.Current = OspCurrentType(dict_xml=dict_xml['Current'])


class OspHydraulicPortType(OspModelDescriptionAbstract):
    Pressure: OspPressureType
    VolumeFlowRate: OspVolumeFlowRateType
    name: str
    _required_keys = ['name']

    def __init__(self, dict_xml: Dict = None, **kwargs):
        super().__init__(dict_xml=dict_xml, **kwargs)

    def to_dict_xml(self):
        return {
            '@name': self.name,
            'Pressure': self.Pressure.to_dict_xml(),
            'VolumeFlowRate': self.VolumeFlowRate.to_dict_xml(),
        }

    def to_dict(self):
        return {
            'Pressure': self.Pressure.to_dict(),
            'Current': self.VolumeFlowRate.to_dict(),
            'name': self.name
        }

    def from_dict_xml(self, dict_xml: Dict):
        self.name = dict_xml['@name']
        self.Pressure = OspPressureType(dict_xml=dict_xml['Pressure'])
        self.VolumeFlowRate = OspVolumeFlowRateType(dict_xml=dict_xml['VolumeFlowRate'])


class OspLinearMechanicalQuasiPortType(OspModelDescriptionAbstract):
    Force: OspForceType
    LinearDisplacement: OspLinearDisplacementType
    name: str
    _required_keys = ['name', 'Force', 'LinearDisplacement']

    def __init__(self, dict_xml: Dict = None, **kwargs):
        super().__init__(dict_xml=dict_xml, **kwargs)

    def from_dict_xml(self, dict_xml: Dict):
        self.name = dict_xml['@name']
        self.Force = OspForceType(dict_xml=dict_xml['Force'])
        self.LinearDisplacement = OspLinearDisplacementType(dict_xml=dict_xml['LinearDisplacement'])

    def to_dict_xml(self):
        return {
            '@name': self.name,
            'Force': self.Force.to_dict_xml(),
            'LinearDisplacement': self.LinearDisplacement.to_dict_xml(),
        }

    def to_dict(self):
        return {
            'Pressure': self.Force.to_dict(),
            'LinearDisplacement': self.LinearDisplacement.to_dict(),
            'name': self.name
        }


class OspAngularMechanicalQuasiPortType(OspModelDescriptionAbstract):
    Torque: OspTorqueType
    AngularDisplacement: OspAngularDisplacementType
    name: str
    _required_keys = ['name', 'Torque', 'AngularDisplacement']

    def __init__(self, dict_xml: Dict = None, **kwargs):
        super().__init__(dict_xml=dict_xml, **kwargs)

    def from_dict_xml(self, dict_xml: Dict):
        self.name = dict_xml['@name']
        self.Torque = OspTorqueType(dict_xml=dict_xml['Torque'])
        self.AngularDisplacement = OspAngularDisplacementType(
            dict_xml=dict_xml['AngularDisplacement']
        )

    def to_dict_xml(self):
        return {
            '@name': self.name,
            'Torque': self.Torque.to_dict_xml(),
            'AngularDisplacement': self.AngularDisplacement.to_dict_xml(),
        }

    def to_dict(self):
        return {
            'Torque': self.Torque.to_dict(),
            'AngularDisplacement': self.AngularDisplacement.to_dict(),
            'name': self.name
        }


class OspElectromagneticQuasiPortType(OspModelDescriptionAbstract):
    Voltage: OspVoltageType
    Charge: OspChargeType
    name: str
    _required_keys = ['name', 'Voltage', 'Charge']

    def __init__(self, dict_xml: Dict = None, **kwargs):
        super().__init__(dict_xml=dict_xml, **kwargs)

    def from_dict_xml(self, dict_xml: Dict):
        self.name = dict_xml['@name']
        self.Voltage = OspVoltageType(dict_xml=dict_xml['Voltage'])
        self.Charge = OspChargeType(dict_xml=dict_xml['Charge'])

    def to_dict_xml(self):
        return {
            '@name': self.name,
            'Voltage': self.Voltage.to_dict_xml(),
            'Charge': self.Charge.to_dict_xml(),
        }

    def to_dict(self):
        return {
            'Voltage': self.Voltage.to_dict(),
            'Charge': self.Charge.to_dict(),
            'name': self.name
        }


class OspHydraulicQuasiPortType(OspModelDescriptionAbstract):
    Pressure: OspPressureType
    Volume: OspVolumeType
    name: str
    _required_keys = ['name', 'Pressure', 'Volume']

    def __init__(self, dict_xml: Dict = None, **kwargs):
        super().__init__(dict_xml=dict_xml, **kwargs)

    def from_dict_xml(self, dict_xml: Dict):
        self.name = dict_xml['@name']
        self.Pressure = OspPressureType(dict_xml=dict_xml['Pressure'])
        self.Volume = OspVolumeType(dict_xml=dict_xml['Volume'])

    def to_dict_xml(self):
        return {
            '@name': self.name,
            'Pressure': self.Pressure.to_dict_xml(),
            'Volume': self.Volume.to_dict_xml(),
        }

    def to_dict(self):
        return {
            'Pressure': self.Pressure.to_dict(),
            'Volume': self.Volume.to_dict(),
            'name': self.name
        }


class OspLinearMechanicalPowerPortType(OspPhysicalTypeBase):
    pass


class OspAngularMechanicalPowerPortType(OspPhysicalTypeBase):
    pass


class OspElectromagneticPowerPortType(OspPhysicalTypeBase):
    pass


class OspHydraulicPowerPortType(OspPhysicalTypeBase):
    pass


class OspGenericType(OspModelDescriptionAbstract):
    name: str
    Variable: List[OspVariableType] = None
    Force: List[OspForceType] = None
    Torque: List[OspTorqueType] = None
    Voltage: List[OspVoltageType] = None
    Pressure: List[OspPressureType] = None
    LinearVelocity: List[OspLinearVelocityType] = None
    AngularVelocity: List[OspAngularVelocityType] = None
    Current: List[OspCurrentType] = None
    VolumeFlowRate: List[OspVolumeFlowRateType] = None
    LinearDisplacement: List[OspLinearDisplacementType] = None
    AngularDisplacement: List[OspAngularDisplacementType] = None
    Charge: List[OspChargeType] = None
    Volume: List[OspVolumeType] = None
    LinearMechanicalPort: List[OspLinearMechanicalPortType] = None
    AngularMechanicalPort: List[OspAngularMechanicalPortType] = None
    ElectromagneticPort: List[OspElectromagneticPortType] = None
    HydraulicPort: List[OspHydraulicPortType] = None
    LinearMechanicalQuasiPort: List[OspLinearMechanicalQuasiPortType] = None
    AngularMechanicalQuasiPort: List[OspAngularMechanicalQuasiPortType] = None
    ElectromagneticQuasiPort: List[OspElectromagneticQuasiPortType] = None
    HydraulicQuasiPort: List[OspHydraulicQuasiPortType] = None
    LinearMechanicalPowerPort: List[OspLinearMechanicalPowerPortType] = None
    AngularMechanicalPowerPort: List[OspAngularMechanicalPowerPortType] = None
    ElectromagneticPowerPort: List[OspElectromagneticPowerPortType] = None
    HydraulicPowerPort: List[OspHydraulicPowerPortType] = None
    _required_keys = ['name']

    def __init__(self, dict_xml: Dict = None, **kwargs):
        super().__init__(dict_xml=dict_xml, **kwargs)

    def from_dict_xml(self, dict_xml: Dict):
        self.name = dict_xml['@name']
        var_group_types = variable_group_types.copy()
        var_group_types['Variable'] = {'class': OspVariableType}
        for type_name, type_class in var_group_types.items():
            if type_name == 'Variable':
                if type_name in dict_xml:
                    self.__setattr__(
                        type_name,
                        [type_class['class'](dict_xml=variable) for variable in dict_xml[type_name]]
                    )
            else:
                if type_name in dict_xml:
                    self.__setattr__(
                        type_name,
                        [type_class['class'](dict_xml=variable) for variable in dict_xml[type_name]]
                    )

    def to_dict_xml(self):
        dict_xml = {'@name': self.name}
        var_group_types = variable_group_types.copy()
        var_group_types['Variable'] = {'class': OspVariableType}
        for var_group in var_group_types:
            if hasattr(self, var_group):
                var_groups_obj = self.__getattribute__(var_group)
                if var_groups_obj:
                    dict_xml[var_group] = [var.to_dict_xml() for var in var_groups_obj]
        return dict_xml

    def to_dict(self):
        dict_obj = {'name': self.name}
        for var_group in variable_group_types:
            if hasattr(self, var_group):
                var_groups_obj = self.__getattribute__(var_group)
                dict_obj[var_group] = None if var_groups_obj is None \
                    else [var.to_dict() for var in var_groups_obj]
        return dict_obj


variable_group_types = {
    'Generic': {'class': OspGenericType, 'field': ['']},
    'Force': {'class': OspForceType, 'field': ['Variable']},
    'Torque': {'class': OspTorqueType, 'field': ['Variable']},
    'Voltage': {'class': OspVoltageType, 'field': ['Variable']},
    'Pressure': {'class': OspPressureType, 'field': ['Variable']},
    'LinearVelocity': {'class': OspLinearVelocityType, 'field': ['Variable']},
    'AngularVelocity': {'class': OspAngularVelocityType, 'field': ['Variable']},
    'Current': {'class': OspCurrentType, 'field': ['Variable']},
    'VolumeFlowRate': {'class': OspVolumeFlowRateType, 'field': ['Variable']},
    'LinearDisplacement': {'class': OspLinearDisplacementType, 'field': ['Variable']},
    'AngularDisplacement': {'class': OspAngularDisplacementType, 'field': ['Variable']},
    'Charge': {'class': OspChargeType, 'field': ['Variable']},
    'Volume': {'class': OspVolumeType, 'field': ['Variable']},
    'LinearMechanicalPort': {
        'class': OspLinearMechanicalPortType,
        'field': ['Force', 'LinearVelocity']
    },
    'AngularMechanicalPort': {
        'class': OspAngularMechanicalPortType,
        'field': ['Torque', 'AngularVelocity']
    },
    'ElectromagneticPort': {'class': OspElectromagneticPortType, 'field': ['Voltage', 'Current']},
    'HydraulicPort': {'class': OspHydraulicPortType, 'field': ['Pressure', 'VolumeFlowRate']},
    'LinearMechanicalQuasiPort': {
        'class': OspLinearMechanicalQuasiPortType, 'field': ['Force', 'LinearDisplacement']
    },
    'AngularMechanicalQuasiPort': {
        'class': OspAngularMechanicalQuasiPortType, 'field': ['Torque', 'AngularDisplacement']
    },
    'ElectromagneticQuasiPort': {
        'class': OspElectromagneticQuasiPortType,
        'field': ['Voltage', 'Charge']
    },
    'HydraulicQuasiPort': {'class': OspHydraulicQuasiPortType, 'field': ['Pressure', 'Volume']},
    'LinearMechanicalPowerPort': {'class': OspLinearMechanicalPowerPortType, 'field': ['Variable']},
    'AngularMechanicalPowerPort': {
        'class': OspAngularMechanicalPowerPortType,
        'field': ['Variable']
    },
    'ElectromagneticPowerPort': {'class': OspElectromagneticPowerPortType, 'field': ['Variable']},
    'HydraulicPowerPort': {'class': OspHydraulicPowerPortType, 'field': ['Variable']},
}

variable_group_types_with_variable_groups = {
    'LinearMechanicalPort': {
        'class': OspLinearMechanicalPortType,
        'field': ['Force', 'LinearVelocity']
    },
    'AngularMechanicalPort': {
        'class': OspAngularMechanicalPortType,
        'field': ['Torque', 'AngularVelocity']
    },
    'ElectromagneticPort': {'class': OspElectromagneticPortType, 'field': ['Voltage', 'Current']},
    'HydraulicPort': {'class': OspHydraulicPortType, 'field': ['Pressure', 'VolumeFlowRate']},
    'LinearMechanicalQuasiPort': {
        'class': OspLinearMechanicalQuasiPortType, 'field': ['Force', 'LinearDisplacement']
    },
    'AngularMechanicalQuasiPort': {
        'class': OspAngularMechanicalQuasiPortType, 'field': ['Torque', 'AngularDisplacement']
    },
    'ElectromagneticQuasiPort': {
        'class': OspElectromagneticQuasiPortType,
        'field': ['Voltage', 'Charge']
    },
    'HydraulicQuasiPort': {'class': OspHydraulicQuasiPortType, 'field': ['Pressure', 'Volume']},
}

variable_group_types_with_variables = {
    'Generic': {'class': OspGenericType, 'field': ['']},
    'Force': {'class': OspForceType, 'field': ['Variable']},
    'Torque': {'class': OspTorqueType, 'field': ['Variable']},
    'Voltage': {'class': OspVoltageType, 'field': ['Variable']},
    'Pressure': {'class': OspPressureType, 'field': ['Variable']},
    'LinearVelocity': {'class': OspLinearVelocityType, 'field': ['Variable']},
    'AngularVelocity': {'class': OspAngularVelocityType, 'field': ['Variable']},
    'Current': {'class': OspCurrentType, 'field': ['Variable']},
    'VolumeFlowRate': {'class': OspVolumeFlowRateType, 'field': ['Variable']},
    'LinearDisplacement': {'class': OspLinearDisplacementType, 'field': ['Variable']},
    'AngularDisplacement': {'class': OspAngularDisplacementType, 'field': ['Variable']},
    'Charge': {'class': OspChargeType, 'field': ['Variable']},
    'Volume': {'class': OspVolumeType, 'field': ['Variable']},
    'LinearMechanicalPowerPort': {
        'class': OspLinearMechanicalPowerPortType, 'field': ['Variable']
    },
    'AngularMechanicalPowerPort': {
        'class': OspAngularMechanicalPowerPortType, 'field': ['Variable']
    },
    'ElectromagneticPowerPort': {'class': OspElectromagneticPowerPortType, 'field': ['Variable']},
    'HydraulicPowerPort': {'class': OspHydraulicPowerPortType, 'field': ['Variable']},
}


class OspVariableGroupsType(OspGenericType):
    name = None
    Generic: List[OspGenericType] = None
    _required_keys = []

    def __init__(self, dict_xml: Dict = None, **kwargs):
        super().__init__(dict_xml=dict_xml, **kwargs)

    def from_dict_xml(self, dict_xml: Dict):
        for type_name, type_class in variable_group_types.items():
            if type_name in dict_xml:
                self.__setattr__(
                    type_name,
                    [type_class['class'](dict_xml=variable) for variable in dict_xml[type_name]]
                )

    def to_dict_xml(self):
        dict_xml_generic = super().to_dict_xml()
        dict_xml_generic.pop("@name")
        keys_to_remove = [key for key, content in dict_xml_generic.items() if content is None]
        for key in keys_to_remove:
            del dict_xml_generic[key]
        if self.Generic is not None:
            dict_xml_generic['Generic'] = [generic.to_dict_xml() for generic in self.Generic]
        return dict_xml_generic

    def to_dict(self):
        dict_xml_generic = super().to_dict()
        dict_xml_generic.pop("name")
        dict_xml = {
            'Generic': None if self.Generic is None
            else [generic.to_dict() for generic in self.Generic]
        }
        dict_xml.update(dict_xml_generic)
        return dict_xml


class OspModelDescription(OspModelDescriptionAbstract):
    VariableGroups: OspVariableGroupsType
    UnitDefinition: OspUnitDefinitionsType = None
    version: str = '0.1'
    _required_keys = ['VariableGroups']

    def __init__(self, dict_xml: Dict = None, xml_source: str = None, **kwargs):
        self.xs = xmlschema.XMLSchema(PATH_TO_XML_SCHEMA)
        if xml_source is not None:
            self.from_xml_str(xml_source)
        else:
            super().__init__(dict_xml=dict_xml, **kwargs)

    def from_dict_xml(self, dict_xml):
        self.VariableGroups = OspVariableGroupsType(dict_xml=dict_xml['VariableGroups'])
        if 'UnitDefinitions' in dict_xml:
            self.UnitDefinition = OspUnitDefinitionsType(dict_xml=dict_xml['UnitDefinitions'])
        self.version = dict_xml['@version']

    def to_dict_xml(self):
        return {
            '@xmlns': self.xs.namespaces['osp'],
            '@version': self.version,
            'UnitDefinitions': None if self.UnitDefinition is None
            else self.UnitDefinition.to_dict_xml(),
            'VariableGroups': None if self.VariableGroups is None
            else self.VariableGroups.to_dict_xml(),
        }

    def from_xml_str(self, xml_source: str):
        """Import XML document of the OSP mode description

        Args:
            xml_source: A path to the file or string content of the model description.
        """
        dict_xml = self.xs.to_dict(xml_source)
        self.from_dict_xml(dict_xml)

    def to_dict(self):
        return {
            'UnitDefinitions': None if self.UnitDefinition is None
            else self.UnitDefinition.to_dict(),
            'VariableGroups': self.VariableGroups.to_dict(),
            'version': self.version
        }

    def to_xml_str(self):
        json_converted = json.dumps(self.to_dict_xml(), indent=2)
        return xmlschema.etree.etree_tostring(xmlschema.from_json(json_converted, self.xs))

    def check_duplicate_name(self, name):
        """Raises an InterfaceError error if there is duplicate name in the existing interfaces"""
        #: Check if there is any duplicates in the name
        for type_name in variable_group_types:
            var_groups = self.VariableGroups.__getattribute__(type_name)
            if var_groups is not None:
                for i, var_group in enumerate(var_groups):
                    if name == var_group.name:
                        msg = 'Error occured while adding the new interface: %s. ' \
                              'The name is already used by another interface: %s:%s' \
                              % (name, type_name, var_group.name)
                        raise InterfaceError(msg)

    def find_interface_by_name(self, name: str) -> Union[InterfaceIndex, None]:

        #: Go through the list to find the name
        for type_name in variable_group_types:
            var_groups = self.VariableGroups.__getattribute__(type_name)
            if var_groups is not None:
                for i, var_group in enumerate(var_groups):
                    if name == var_group.name:
                        return InterfaceIndex(type_name=type_name, index=i)
        return None

    def add_interface(
            self, new_interface: Union[
                OspVariableType, OspGenericType, OspForceType, OspTorqueType, OspVoltageType,
                OspPressureType, OspLinearVelocityType, OspAngularVelocityType, OspCurrentType,
                OspVolumeFlowRateType, OspLinearDisplacementType, OspAngularDisplacementType,
                OspChargeType, OspVolumeType, OspLinearMechanicalPortType,
                OspAngularMechanicalPortType, OspElectromagneticPortType,
                OspHydraulicPortType, OspLinearMechanicalQuasiPortType,
                OspAngularMechanicalQuasiPortType, OspElectromagneticQuasiPortType,
                OspHydraulicQuasiPortType, OspLinearMechanicalPowerPortType,
                OspAngularMechanicalPowerPortType, OspElectromagneticPowerPortType,
                OspHydraulicPowerPortType
            ]
    ):
        type_name_new = find_type_of_variable_groups(new_interface)

        self.check_duplicate_name(new_interface.name)

        interfaces = self.VariableGroups.__getattribute__(type_name_new)

        if interfaces is None:
            self.VariableGroups.__setattr__(type_name_new, [new_interface])
        else:
            interfaces.append(new_interface)
            self.VariableGroups.__setattr__(type_name_new, interfaces)

    def update_interface(
            self, new_interface: Union[
                OspVariableType, OspGenericType, OspForceType, OspTorqueType, OspVoltageType,
                OspPressureType, OspLinearVelocityType, OspAngularVelocityType, OspCurrentType,
                OspVolumeFlowRateType, OspLinearDisplacementType, OspAngularDisplacementType,
                OspChargeType, OspVolumeType, OspLinearMechanicalPortType,
                OspAngularMechanicalPortType, OspElectromagneticPortType,
                OspHydraulicPortType, OspLinearMechanicalQuasiPortType,
                OspAngularMechanicalQuasiPortType, OspElectromagneticQuasiPortType,
                OspHydraulicQuasiPortType, OspLinearMechanicalPowerPortType,
                OspAngularMechanicalPowerPortType, OspElectromagneticPowerPortType,
                OspHydraulicPowerPortType
            ], old_name: str
    ):
        self.delete_interface(old_name)
        self.add_interface(new_interface)

    def delete_interface(
            self,
            interface_name: str,
    ):
        interface_index = self.find_interface_by_name(interface_name)
        var_groups = self.VariableGroups.__getattribute__(interface_index.type_name)
        deleted_var_group = var_groups.pop(interface_index.index)
        var_groups = None if len(var_groups) == 0 else var_groups
        self.VariableGroups.__setattr__(interface_index.type_name, var_groups)
        return deleted_var_group

    def get_variables(self):
        osp_variables = []
        for var_group in self.get_variable_group_with_variables():
            osp_variables.extend(var_group.Variable)
        return osp_variables

    def get_variable_group_with_variables(self):
        osp_variable_group_with_variables = []
        for var_group_name in variable_group_types:
            if getattr(self.VariableGroups, var_group_name):
                var_group = getattr(self.VariableGroups, var_group_name)[0]
                if var_group_name in variable_group_types_with_variable_groups:
                    subtypes = variable_group_types_with_variable_groups[var_group_name]['field']
                    for subtype_name in subtypes:
                        osp_variable_group_with_variables.append(getattr(var_group, subtype_name))
                elif var_group_name in variable_group_types_with_variables:
                    osp_variable_group_with_variables.append(var_group)
        return osp_variable_group_with_variables


def get_osp_model_description_type_from_json(json_text: str) -> OspModelDescription:
    dict_xml = json.JSONDecoder().decode(json_text)
    return OspModelDescription(dict_xml=dict_xml)


def find_type_of_variable_groups(interface: Union[
    OspVariableType, OspGenericType, OspForceType, OspTorqueType, OspVoltageType, OspPressureType,
    OspLinearVelocityType, OspAngularVelocityType, OspCurrentType, OspVolumeFlowRateType,
    OspLinearDisplacementType, OspAngularDisplacementType, OspChargeType, OspVolumeType,
    OspLinearMechanicalPortType, OspAngularMechanicalPortType, OspElectromagneticPortType,
    OspHydraulicPortType, OspLinearMechanicalQuasiPortType, OspAngularMechanicalQuasiPortType,
    OspElectromagneticQuasiPortType, OspHydraulicQuasiPortType, OspLinearMechanicalPowerPortType,
    OspAngularMechanicalPowerPortType, OspElectromagneticPowerPortType, OspHydraulicPowerPortType
]) -> str:
    type_list = list(variable_group_types.keys())
    class_list = list(variable_group_types.values())

    #: Find the index for the type of interface
    idx_type = None
    for i, class_type in enumerate(class_list):
        if type(interface) is class_type['class']:
            idx_type = i
            break

    return type_list[idx_type]
