"""
RIFT Language Environment

Scope and variable management with support for:
- Lexical scoping
- Closures
- Immutable (let) and mutable (mut) bindings
- Constants (const)
- Variable shadowing
"""

from typing import Any, Dict, Optional, Set, Callable
from .errors import NameError, AssignmentError


class Environment:
    """
    Environment for variable storage and scope management.
    
    Implements lexical scoping with proper closure support.
    Each environment has a reference to its parent (enclosing) scope.
    """
    
    def __init__(self, parent: Optional['Environment'] = None, name: str = "global"):
        self.parent = parent
        self.name = name
        self._variables: Dict[str, Any] = {}
        self._immutables: Set[str] = set()  # Variables declared with 'let'
        self._constants: Set[str] = set()   # Variables declared with 'const'
        self._types: Dict[str, str] = {}    # Type hints for variables
    
    def define(self, name: str, value: Any, mutable: bool = True, 
               constant: bool = False, type_hint: Optional[str] = None) -> None:
        """
        Define a new variable in the current scope.
        
        Args:
            name: Variable name
            value: Initial value
            mutable: If False, variable cannot be reassigned (let)
            constant: If True, variable is a compile-time constant (const)
            type_hint: Optional type annotation
        """
        self._variables[name] = value
        
        if not mutable:
            self._immutables.add(name)
        
        if constant:
            self._constants.add(name)
            self._immutables.add(name)  # Constants are also immutable
        
        if type_hint:
            self._types[name] = type_hint
    
    def get(self, name: str) -> Any:
        """
        Get a variable's value, searching up the scope chain.
        
        Args:
            name: Variable name
            
        Returns:
            The variable's value
            
        Raises:
            NameError: If variable is not defined
        """
        if name in self._variables:
            return self._variables[name]
        
        if self.parent:
            return self.parent.get(name)
        
        raise NameError(f"Undefined variable '{name}'")
    
    def set(self, name: str, value: Any) -> None:
        """
        Set a variable's value, searching up the scope chain.
        
        Args:
            name: Variable name
            value: New value
            
        Raises:
            NameError: If variable is not defined
            AssignmentError: If variable is immutable
        """
        # Check current scope first
        if name in self._variables:
            if name in self._constants:
                raise AssignmentError(f"Cannot reassign constant '{name}'")
            if name in self._immutables:
                raise AssignmentError(f"Cannot reassign immutable variable '{name}' (use 'mut' to make it mutable)")
            self._variables[name] = value
            return
        
        # Check parent scopes
        if self.parent:
            self.parent.set(name, value)
            return
        
        raise NameError(f"Undefined variable '{name}'")
    
    def assign_at(self, name: str, value: Any) -> None:
        """
        Assign to a variable in the current scope only.
        Used for updating properties or local assignments.
        """
        if name in self._constants:
            raise AssignmentError(f"Cannot reassign constant '{name}'")
        if name in self._immutables:
            raise AssignmentError(f"Cannot reassign immutable variable '{name}'")
        self._variables[name] = value
    
    def has(self, name: str, local_only: bool = False) -> bool:
        """Check if a variable is defined."""
        if name in self._variables:
            return True
        if not local_only and self.parent:
            return self.parent.has(name)
        return False
    
    def is_immutable(self, name: str) -> bool:
        """Check if a variable is immutable."""
        if name in self._immutables:
            return True
        if self.parent:
            return self.parent.is_immutable(name)
        return False
    
    def is_constant(self, name: str) -> bool:
        """Check if a variable is a constant."""
        if name in self._constants:
            return True
        if self.parent:
            return self.parent.is_constant(name)
        return False
    
    def get_type_hint(self, name: str) -> Optional[str]:
        """Get the type hint for a variable."""
        if name in self._types:
            return self._types[name]
        if self.parent:
            return self.parent.get_type_hint(name)
        return None
    
    def child(self, name: str = "local") -> 'Environment':
        """Create a child scope."""
        return Environment(parent=self, name=name)
    
    def copy(self) -> 'Environment':
        """Create a shallow copy of this environment (for closures)."""
        env = Environment(parent=self.parent, name=self.name)
        env._variables = self._variables.copy()
        env._immutables = self._immutables.copy()
        env._constants = self._constants.copy()
        env._types = self._types.copy()
        return env
    
    def __repr__(self) -> str:
        vars_str = ", ".join(f"{k}={v!r}" for k, v in self._variables.items())
        return f"<Environment {self.name}: {vars_str}>"


class GlobalEnvironment(Environment):
    """
    Global environment with built-in functions and values.
    """
    
    def __init__(self):
        super().__init__(parent=None, name="global")
        self._setup_builtins()
    
    def _setup_builtins(self):
        """Initialize built-in functions and values."""
        # Built-in constants
        self.define('yes', True, mutable=False, constant=True)
        self.define('no', False, mutable=False, constant=True)
        self.define('none', None, mutable=False, constant=True)
        
        # Built-in functions will be added by the interpreter
        # to have access to the interpreter instance


def create_global_environment() -> GlobalEnvironment:
    """Factory function to create a new global environment."""
    return GlobalEnvironment()
