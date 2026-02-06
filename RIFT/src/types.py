"""
RIFT Language Type System

Dynamic + gradual type system with optional type hints and runtime type checking.
"""

from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union


class RiftType(Enum):
    """Core RIFT types."""
    TEXT = auto()      # String type
    NUM = auto()       # Number type (int or float)
    BOOL = auto()      # Boolean type
    LIST = auto()      # Array/list type
    MAP = auto()       # Object/dictionary type
    NONE = auto()      # Null/none type
    CONDUIT = auto()   # Function type
    CLASS = auto()     # Class type
    INSTANCE = auto()  # Class instance type
    ANY = auto()       # Any type (for untyped values)
    GENERATOR = auto() # Generator type


# Type name mappings from RIFT syntax to RiftType
TYPE_NAMES = {
    'text': RiftType.TEXT,
    'num': RiftType.NUM,
    'bool': RiftType.BOOL,
    'list': RiftType.LIST,
    'map': RiftType.MAP,
    'none': RiftType.NONE,
    'conduit': RiftType.CONDUIT,
    'any': RiftType.ANY,
}


def get_type(value: Any) -> RiftType:
    """Determine the RIFT type of a Python value."""
    if value is None:
        return RiftType.NONE
    if isinstance(value, bool):
        return RiftType.BOOL
    if isinstance(value, (int, float)):
        return RiftType.NUM
    if isinstance(value, str):
        return RiftType.TEXT
    if isinstance(value, list):
        return RiftType.LIST
    if isinstance(value, dict):
        return RiftType.MAP
    if callable(value):
        return RiftType.CONDUIT
    if hasattr(value, '__rift_class__'):
        return RiftType.INSTANCE
    return RiftType.ANY


def type_name(value: Any) -> str:
    """Get human-readable type name of a value."""
    rift_type = get_type(value)
    for name, t in TYPE_NAMES.items():
        if t == rift_type:
            return name
    if rift_type == RiftType.INSTANCE:
        return f"instance of {getattr(value, '__rift_class__', 'unknown')}"
    if rift_type == RiftType.GENERATOR:
        return "generator"
    return "any"


def check_type(value: Any, expected_type: str) -> bool:
    """Check if value matches expected type."""
    if expected_type not in TYPE_NAMES:
        return True  # Unknown type, allow it
    
    expected = TYPE_NAMES[expected_type]
    if expected == RiftType.ANY:
        return True
    
    actual = get_type(value)
    return actual == expected


def coerce_type(value: Any, target_type: str) -> Any:
    """Attempt to coerce value to target type."""
    if target_type == 'text':
        return str(value) if value is not None else "none"
    if target_type == 'num':
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            try:
                return float(value) if '.' in value else int(value)
            except ValueError:
                return 0
        if isinstance(value, bool):
            return 1 if value else 0
        return 0
    if target_type == 'bool':
        return bool(value)
    if target_type == 'list':
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            return list(value.items())
        if isinstance(value, str):
            return list(value)
        return [value]
    if target_type == 'map':
        if isinstance(value, dict):
            return value
        if isinstance(value, list):
            return {i: v for i, v in enumerate(value)}
        return {'value': value}
    return value


class RiftValue:
    """Wrapper for RIFT values with type information."""
    
    def __init__(self, value: Any, type_hint: Optional[str] = None):
        self.value = value
        self.type_hint = type_hint
        self._type = get_type(value)
    
    @property
    def rift_type(self) -> RiftType:
        return self._type
    
    def matches_type(self, type_name: str) -> bool:
        return check_type(self.value, type_name)
    
    def __repr__(self):
        return f"RiftValue({self.value!r}, type={self.type_hint})"


class RiftClass:
    """Represents a RIFT class definition."""
    
    def __init__(self, name: str, methods: Dict, properties: Dict,
                 parent: Optional['RiftClass'] = None,
                 static_methods: Optional[Dict] = None,
                 static_properties: Optional[Dict] = None):
        self.name = name
        self.methods = methods
        self.properties = properties
        self.parent = parent
        self.static_methods = static_methods or {}
        self.static_properties = static_properties or {}
    
    def __repr__(self):
        return f"<class {self.name}>"


class RiftInstance:
    """Represents an instance of a RIFT class."""
    
    def __init__(self, rift_class: RiftClass):
        self.__rift_class__ = rift_class.name
        self._class = rift_class
        self._properties: Dict[str, Any] = {}
        # Copy default properties from class
        for name, value in rift_class.properties.items():
            self._properties[name] = value
    
    def get_property(self, name: str) -> Any:
        if name in self._properties:
            return self._properties[name]
        # Check parent classes
        parent = self._class.parent
        while parent:
            if name in parent.properties:
                return parent.properties[name]
            parent = parent.parent
        raise AttributeError(f"'{self._class.name}' has no property '{name}'")
    
    def set_property(self, name: str, value: Any):
        self._properties[name] = value
    
    def get_method(self, name: str):
        if name in self._class.methods:
            return self._class.methods[name]
        # Check parent classes
        parent = self._class.parent
        while parent:
            if name in parent.methods:
                return parent.methods[name]
            parent = parent.parent
        raise AttributeError(f"'{self._class.name}' has no method '{name}'")
    
    def __repr__(self):
        return f"<{self._class.name} instance>"


class RiftGenerator:
    """Represents a RIFT generator."""
    
    def __init__(self, func, env):
        self.func = func
        self.env = env
        self.started = False
        self.finished = False
        self._iterator = None
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.finished:
            raise StopIteration
        if not self.started:
            self.started = True
            self._iterator = self.func(self.env)
        try:
            return next(self._iterator)
        except StopIteration:
            self.finished = True
            raise
