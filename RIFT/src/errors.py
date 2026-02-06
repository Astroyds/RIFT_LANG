"""
RIFT Language Error Classes

Custom error types for the RIFT programming language with detailed
error messages and stack trace support.
"""


class RiftError(Exception):
    """Base class for all RIFT language errors."""
    
    def __init__(self, message, line=None, column=None, filename=None):
        self.message = message
        self.line = line
        self.column = column
        self.filename = filename
        super().__init__(self._format_message())
    
    def _format_message(self):
        location = ""
        if self.filename:
            location += f"File '{self.filename}'"
        if self.line is not None:
            location += f", line {self.line}"
        if self.column is not None:
            location += f", column {self.column}"
        if location:
            return f"{location}: {self.message}"
        return self.message


class LexerError(RiftError):
    """Error during tokenization phase."""
    pass


class ParseError(RiftError):
    """Error during parsing phase."""
    pass


class RuntimeError(RiftError):
    """Error during execution phase."""
    pass


class TypeError(RiftError):
    """Type-related runtime error."""
    pass


class NameError(RiftError):
    """Undefined variable or function error."""
    pass


class ImportError(RiftError):
    """Error during module import."""
    pass


class AssignmentError(RiftError):
    """Error when assigning to immutable variable."""
    pass


class IndexError(RiftError):
    """Index out of bounds error."""
    pass


class KeyError(RiftError):
    """Key not found in map error."""
    pass


class DivisionByZeroError(RiftError):
    """Division by zero error."""
    pass


class ArgumentError(RiftError):
    """Wrong number or type of arguments."""
    pass


class StopIteration(RiftError):
    """Generator exhausted signal."""
    pass


class BreakSignal(Exception):
    """Signal for breaking out of loops."""
    pass


class ContinueSignal(Exception):
    """Signal for continuing to next iteration."""
    pass


class ReturnSignal(Exception):
    """Signal for returning from functions."""
    
    def __init__(self, value=None):
        self.value = value
        super().__init__()


class YieldSignal(Exception):
    """Signal for yielding from generators."""
    
    def __init__(self, value=None):
        self.value = value
        super().__init__()
