"""
RIFT Standard Library - JSON Module

JSON parsing and stringification utilities.
"""

import json
from typing import Any, Dict


def create_json_module(interpreter) -> Dict[str, Any]:
    """Create the JSON module for RIFT."""
    
    def json_parse(string: str) -> Any:
        """Parse a JSON string into a RIFT value."""
        try:
            return json.loads(string)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON parse error: {e}")
    
    def json_stringify(data: Any, indent: int = None) -> str:
        """Convert a RIFT value to JSON string."""
        try:
            return json.dumps(data, indent=indent, default=_json_serializer)
        except (TypeError, ValueError) as e:
            raise ValueError(f"JSON stringify error: {e}")
    
    def json_pretty(data: Any, indent: int = 2) -> str:
        """Pretty-print a RIFT value as JSON."""
        return json_stringify(data, indent=indent)
    
    def _json_serializer(obj):
        """Custom serializer for RIFT objects."""
        if hasattr(obj, '_properties'):
            # RiftInstance
            return obj._properties
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)
    
    return {
        'parse': json_parse,
        'stringify': json_stringify,
        'pretty': json_pretty,
    }
