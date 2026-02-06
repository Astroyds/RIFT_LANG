"""
RIFT Language AST Nodes

Abstract Syntax Tree node definitions for the RIFT language.
Each node represents a syntactic construct in the language.
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict, Union


@dataclass
class Node:
    """Base class for all AST nodes."""
    line: int = 0
    column: int = 0


# ============================================================================
# Expressions
# ============================================================================

@dataclass
class Literal(Node):
    """Literal values: numbers, strings, booleans, none."""
    value: Any = None


@dataclass
class Identifier(Node):
    """Variable or function name reference."""
    name: str = ""


@dataclass
class BinaryOp(Node):
    """Binary operation: left op right."""
    operator: str = ""
    left: Node = None
    right: Node = None


@dataclass
class UnaryOp(Node):
    """Unary operation: op operand."""
    operator: str = ""
    operand: Node = None


@dataclass
class Comparison(Node):
    """Comparison chain: a < b < c."""
    operators: List[str] = field(default_factory=list)
    operands: List[Node] = field(default_factory=list)


@dataclass
class LogicalOp(Node):
    """Logical operation: and, or."""
    operator: str = ""
    left: Node = None
    right: Node = None


@dataclass
class Assignment(Node):
    """Assignment expression."""
    target: Node = None
    value: Node = None
    operator: str = "="  # =, +=, -=, *=, /=


@dataclass
class Call(Node):
    """Function call."""
    callee: Node = None
    arguments: List[Node] = field(default_factory=list)


@dataclass
class MemberAccess(Node):
    """Member access: object.property or object?.property."""
    object: Node = None
    property: str = ""
    safe: bool = False  # True for ?. operator


@dataclass
class IndexAccess(Node):
    """Index access: array[index] or array?[index]."""
    object: Node = None
    index: Node = None
    safe: bool = False  # True for ?[ operator


@dataclass
class StaticAccess(Node):
    """Static member access: Class::method."""
    object: Node = None
    property: str = ""


@dataclass
class ListLiteral(Node):
    """List/array literal: [1, 2, 3]."""
    elements: List[Node] = field(default_factory=list)


@dataclass
class MapLiteral(Node):
    """Map/object literal: {key: value}."""
    entries: List[tuple] = field(default_factory=list)  # [(key, value), ...]


@dataclass
class Range(Node):
    """Range expression: start..end or start to end."""
    start: Node = None
    end: Node = None
    inclusive: bool = True


@dataclass
class Pipeline(Node):
    """Pipeline expression: value -> transform."""
    value: Node = None
    stages: List[Node] = field(default_factory=list)
    async_: bool = False  # True for ~> operator


@dataclass
class Lambda(Node):
    """Lambda expression: (params) => body or x => body."""
    params: List['Parameter'] = field(default_factory=list)
    body: Node = None


@dataclass
class Ternary(Node):
    """Ternary expression: condition ? then : else."""
    condition: Node = None
    then_expr: Node = None
    else_expr: Node = None


@dataclass
class NullCoalesce(Node):
    """Null coalescing: value ?? default."""
    left: Node = None
    right: Node = None


@dataclass
class SpreadElement(Node):
    """Spread element: ...iterable."""
    argument: Node = None


@dataclass
class Await(Node):
    """Await expression: wait promise."""
    expression: Node = None


@dataclass
class Yield(Node):
    """Yield expression: yield value."""
    expression: Node = None


@dataclass
class TemplateString(Node):
    """Template string with interpolation."""
    parts: List[Node] = field(default_factory=list)  # Mix of strings and expressions


@dataclass
class Me(Node):
    """Self reference in class methods."""
    pass


@dataclass
class Parent(Node):
    """Super/parent reference in class methods."""
    pass


# ============================================================================
# Statements
# ============================================================================

@dataclass
class Program(Node):
    """Root node of the AST."""
    body: List[Node] = field(default_factory=list)


@dataclass
class Block(Node):
    """Block of statements: { ... }."""
    statements: List[Node] = field(default_factory=list)


@dataclass
class ExpressionStatement(Node):
    """Expression as a statement."""
    expression: Node = None


@dataclass
class Parameter(Node):
    """Function parameter."""
    name: str = ""
    type_hint: Optional[str] = None
    default: Optional[Node] = None
    rest: bool = False  # True for ...param


@dataclass
class VariableDeclaration(Node):
    """Variable declaration: let/mut/const."""
    kind: str = "let"  # let, mut, const
    name: str = ""
    type_hint: Optional[str] = None
    value: Optional[Node] = None


@dataclass
class DestructuringDeclaration(Node):
    """Destructuring declaration: let [a, b] = array or let {x, y} = obj."""
    kind: str = "let"
    pattern: Node = None  # ListPattern or MapPattern
    value: Node = None


@dataclass
class ListPattern(Node):
    """List destructuring pattern: [a, b, ...rest]."""
    elements: List[Node] = field(default_factory=list)  # Identifiers or nested patterns


@dataclass
class MapPattern(Node):
    """Map/object destructuring pattern: {a, b: alias}."""
    entries: List[tuple] = field(default_factory=list)  # [(key, alias), ...]


@dataclass
class FunctionDeclaration(Node):
    """Function declaration: conduit name(params) { body }."""
    name: str = ""
    params: List[Parameter] = field(default_factory=list)
    body: Node = None
    async_: bool = False
    generator: bool = False
    return_type: Optional[str] = None


@dataclass
class IfStatement(Node):
    """If statement: if condition { then } else { else }."""
    condition: Node = None
    then_branch: Node = None
    else_branch: Optional[Node] = None


@dataclass
class WhileStatement(Node):
    """While loop: while condition { body }."""
    condition: Node = None
    body: Node = None


@dataclass
class RepeatStatement(Node):
    """For loop: repeat item in iterable { body }."""
    variable: str = ""
    index_var: Optional[str] = None  # For repeat (index, item) in ...
    iterable: Node = None
    body: Node = None


@dataclass
class CheckStatement(Node):
    """Pattern matching: check value { patterns }."""
    value: Node = None
    cases: List['CheckCase'] = field(default_factory=list)


@dataclass
class CheckCase(Node):
    """A case in pattern matching."""
    pattern: Node = None
    guard: Optional[Node] = None  # when condition
    body: Node = None


@dataclass
class TryStatement(Node):
    """Try/catch/finally: try { } catch e { } finally { }."""
    try_block: Node = None
    catch_var: Optional[str] = None
    catch_block: Optional[Node] = None
    finally_block: Optional[Node] = None


@dataclass
class FailStatement(Node):
    """Throw error: fail error."""
    error: Node = None


@dataclass
class GiveStatement(Node):
    """Return statement: give value."""
    value: Optional[Node] = None


@dataclass
class StopStatement(Node):
    """Break statement: stop."""
    pass


@dataclass
class NextStatement(Node):
    """Continue statement: next."""
    pass


# ============================================================================
# Classes
# ============================================================================

@dataclass
class ClassDeclaration(Node):
    """Class declaration: make ClassName extend Parent { body }."""
    name: str = ""
    parent: Optional[str] = None
    body: List[Node] = field(default_factory=list)


@dataclass
class MethodDeclaration(Node):
    """Method in a class."""
    name: str = ""
    params: List[Parameter] = field(default_factory=list)
    body: Node = None
    async_: bool = False
    static: bool = False
    is_getter: bool = False
    is_setter: bool = False


@dataclass
class PropertyDeclaration(Node):
    """Property in a class."""
    name: str = ""
    type_hint: Optional[str] = None
    value: Optional[Node] = None
    static: bool = False


@dataclass
class Constructor(Node):
    """Constructor: build(params) { body }."""
    params: List[Parameter] = field(default_factory=list)
    body: Node = None


# ============================================================================
# Modules
# ============================================================================

@dataclass
class ImportStatement(Node):
    """Import statement: grab module or grab module.item."""
    module: str = ""
    items: List[str] = field(default_factory=list)  # Specific items to import
    alias: Optional[str] = None  # For: grab module as alias
    wildcard: bool = False  # For: grab module.*


@dataclass
class ExportStatement(Node):
    """Export statement: share name or share { items }."""
    declaration: Optional[Node] = None  # For: share let x = 5
    names: List[str] = field(default_factory=list)  # For: share { a, b }


# ============================================================================
# Pattern Matching Patterns
# ============================================================================

@dataclass
class LiteralPattern(Node):
    """Match a literal value."""
    value: Any = None


@dataclass
class RangePattern(Node):
    """Match a range: 1..10."""
    start: Node = None
    end: Node = None


@dataclass
class TypePattern(Node):
    """Match a type: is text."""
    type_name: str = ""


@dataclass
class BindingPattern(Node):
    """Capture a value: x."""
    name: str = ""


@dataclass  
class WildcardPattern(Node):
    """Match anything: _."""
    pass


@dataclass
class GuardPattern(Node):
    """Pattern with guard: pattern when condition."""
    pattern: Node = None
    guard: Node = None
