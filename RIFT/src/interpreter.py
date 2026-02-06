"""
RIFT Language Interpreter

Execution engine that evaluates AST nodes and produces results.
Implements:
- Recursive AST evaluation
- Proper scope chain with closures
- Auto-return (last expression in conduit)
- Pipeline execution
- Optional chaining and null coalescing
- Pattern matching
"""

import asyncio
from typing import Any, Dict, List, Optional, Callable, Union
from functools import partial

from . import ast_nodes as ast
from .environment import Environment, GlobalEnvironment, create_global_environment
from .errors import (
    RuntimeError, TypeError, NameError, AssignmentError,
    ArgumentError, DivisionByZeroError, BreakSignal, ContinueSignal,
    ReturnSignal, YieldSignal, RiftError
)
from .types import (
    RiftClass, RiftInstance, RiftGenerator, RiftType,
    get_type, type_name, check_type
)


class RiftFunction:
    """Wrapper for RIFT function definitions."""
    
    def __init__(self, declaration: ast.FunctionDeclaration, closure: Environment,
                 is_method: bool = False):
        self.declaration = declaration
        self.closure = closure
        self.is_method = is_method
        self.is_async = declaration.async_
        self.is_generator = declaration.generator
    
    def __repr__(self):
        return f"<conduit {self.declaration.name}>"


class RiftLambda:
    """Wrapper for RIFT lambda expressions."""
    
    def __init__(self, node: ast.Lambda, closure: Environment):
        self.node = node
        self.closure = closure
    
    def __repr__(self):
        return "<lambda>"


class RiftBoundMethod:
    """Method bound to an instance."""
    
    def __init__(self, instance: RiftInstance, method: RiftFunction):
        self.instance = instance
        self.method = method
    
    def __repr__(self):
        return f"<bound method {self.method.declaration.name}>"


class Interpreter:
    """
    RIFT language interpreter.
    
    Executes AST nodes in a given environment and returns results.
    """
    
    def __init__(self, env: Optional[Environment] = None):
        self.global_env = env or create_global_environment()
        self.current_env = self.global_env
        self.modules: Dict[str, Dict[str, Any]] = {}
        self._setup_builtins()
    
    def _setup_builtins(self):
        """Setup built-in functions."""
        builtins = {
            'print': self._builtin_print,
            'input': self._builtin_input,
            'len': self._builtin_len,
            'type': self._builtin_type,
            'range': self._builtin_range,
            'map': self._builtin_map,
            'filter': self._builtin_filter,
            'reduce': self._builtin_reduce,
            'sort': self._builtin_sort,
            'reverse': self._builtin_reverse,
            'keys': self._builtin_keys,
            'values': self._builtin_values,
            'entries': self._builtin_entries,
            'split': self._builtin_split,
            'join': self._builtin_join,
            'now': self._builtin_now,
            'sleep': self._builtin_sleep,
            'str': self._builtin_str,
            'num': self._builtin_num,
            'int': self._builtin_int,
            'float': self._builtin_float,
            'bool': self._builtin_bool,
            'list': self._builtin_list,
            'sum': self._builtin_sum,
            'min': self._builtin_min,
            'max': self._builtin_max,
            'abs': self._builtin_abs,
            'round': self._builtin_round,
            'floor': self._builtin_floor,
            'ceil': self._builtin_ceil,
            'push': self._builtin_push,
            'pop': self._builtin_pop,
            'shift': self._builtin_shift,
            'unshift': self._builtin_unshift,
            'slice': self._builtin_slice,
            'indexOf': self._builtin_index_of,
            'includes': self._builtin_includes,
            'find': self._builtin_find,
            'every': self._builtin_every,
            'some': self._builtin_some,
            'concat': self._builtin_concat,
            'flat': self._builtin_flat,
            'fill': self._builtin_fill,
            'upper': self._builtin_upper,
            'lower': self._builtin_lower,
            'trim': self._builtin_trim,
            'replace': self._builtin_replace,
            'startsWith': self._builtin_starts_with,
            'endsWith': self._builtin_ends_with,
            'charAt': self._builtin_char_at,
            'substring': self._builtin_substring,
            'repeat': self._builtin_repeat_str,
            'padStart': self._builtin_pad_start,
            'padEnd': self._builtin_pad_end,
        }
        
        for name, func in builtins.items():
            self.global_env.define(name, func, mutable=False)
    
    # ========================================================================
    # Main Evaluation
    # ========================================================================
    
    def execute(self, program: ast.Program) -> Any:
        """Execute a program and return the result."""
        result = None
        for node in program.body:
            result = self.evaluate(node)
        return result
    
    def evaluate(self, node: ast.Node) -> Any:
        """Evaluate an AST node."""
        if node is None:
            return None
        
        method_name = f'_eval_{node.__class__.__name__}'
        method = getattr(self, method_name, None)
        
        if method is None:
            raise RuntimeError(f"Unknown node type: {node.__class__.__name__}")
        
        return method(node)
    
    # ========================================================================
    # Statements
    # ========================================================================
    
    def _eval_Program(self, node: ast.Program) -> Any:
        return self.execute(node)
    
    def _eval_Block(self, node: ast.Block) -> Any:
        """Evaluate a block of statements."""
        result = None
        for stmt in node.statements:
            result = self.evaluate(stmt)
        return result
    
    def _eval_ExpressionStatement(self, node: ast.ExpressionStatement) -> Any:
        return self.evaluate(node.expression)
    
    def _eval_VariableDeclaration(self, node: ast.VariableDeclaration) -> None:
        """Handle let/mut/const declarations."""
        value = None
        if node.value is not None:
            value = self.evaluate(node.value)
        
        # Type checking if type hint is provided
        if node.type_hint and value is not None:
            if not check_type(value, node.type_hint):
                actual = type_name(value)
                raise TypeError(
                    f"Expected type '{node.type_hint}', got '{actual}'",
                    node.line, node.column
                )
        
        mutable = node.kind == 'mut'
        constant = node.kind == 'const'
        
        self.current_env.define(
            node.name,
            value,
            mutable=mutable,
            constant=constant,
            type_hint=node.type_hint
        )
    
    def _eval_DestructuringDeclaration(self, node: ast.DestructuringDeclaration) -> None:
        """Handle destructuring: let [a, b] = ... or let {x, y} = ..."""
        value = self.evaluate(node.value)
        mutable = node.kind == 'mut'
        constant = node.kind == 'const'
        
        if isinstance(node.pattern, ast.ListPattern):
            self._destructure_list(node.pattern, value, mutable, constant)
        elif isinstance(node.pattern, ast.MapPattern):
            self._destructure_map(node.pattern, value, mutable, constant)
    
    def _destructure_list(self, pattern: ast.ListPattern, value: Any,
                          mutable: bool, constant: bool) -> None:
        """Destructure a list into variables."""
        if not isinstance(value, (list, tuple)):
            raise TypeError(f"Cannot destructure non-list value: {type_name(value)}")
        
        value = list(value)
        
        for i, elem in enumerate(pattern.elements):
            if isinstance(elem, ast.SpreadElement):
                # Rest of the list
                name = elem.argument.name
                self.current_env.define(name, value[i:], mutable=mutable, constant=constant)
                break
            elif isinstance(elem, ast.Identifier):
                if i < len(value):
                    self.current_env.define(elem.name, value[i], mutable=mutable, constant=constant)
                else:
                    self.current_env.define(elem.name, None, mutable=mutable, constant=constant)
    
    def _destructure_map(self, pattern: ast.MapPattern, value: Any,
                         mutable: bool, constant: bool) -> None:
        """Destructure a map into variables."""
        if not isinstance(value, dict):
            raise TypeError(f"Cannot destructure non-map value: {type_name(value)}")
        
        for key, alias in pattern.entries:
            val = value.get(key, None)
            self.current_env.define(alias, val, mutable=mutable, constant=constant)
    
    def _eval_FunctionDeclaration(self, node: ast.FunctionDeclaration) -> RiftFunction:
        """Define a function."""
        func = RiftFunction(node, self.current_env)
        self.current_env.define(node.name, func, mutable=False)
        return func
    
    def _eval_IfStatement(self, node: ast.IfStatement) -> Any:
        """Evaluate if statement."""
        condition = self.evaluate(node.condition)
        
        if self._is_truthy(condition):
            return self.evaluate(node.then_branch)
        elif node.else_branch:
            return self.evaluate(node.else_branch)
        
        return None
    
    def _eval_WhileStatement(self, node: ast.WhileStatement) -> Any:
        """Evaluate while loop."""
        result = None
        
        while self._is_truthy(self.evaluate(node.condition)):
            try:
                result = self.evaluate(node.body)
            except BreakSignal:
                break
            except ContinueSignal:
                continue
        
        return result
    
    def _eval_RepeatStatement(self, node: ast.RepeatStatement) -> Any:
        """Evaluate repeat (for) loop."""
        iterable = self.evaluate(node.iterable)
        result = None
        
        # Make iterable if it's a range
        if isinstance(iterable, range):
            iterable = list(iterable)
        elif isinstance(iterable, str):
            iterable = list(iterable)
        elif isinstance(iterable, dict):
            iterable = list(iterable.items())
        
        if not hasattr(iterable, '__iter__'):
            raise TypeError(f"Cannot iterate over {type_name(iterable)}")
        
        env = self.current_env.child("repeat")
        prev_env = self.current_env
        self.current_env = env
        
        try:
            for i, item in enumerate(iterable):
                if node.index_var:
                    env.define(node.index_var, i, mutable=False)
                env.define(node.variable, item, mutable=False)
                
                try:
                    result = self.evaluate(node.body)
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue
        finally:
            self.current_env = prev_env
        
        return result
    
    def _eval_CheckStatement(self, node: ast.CheckStatement) -> Any:
        """Evaluate pattern matching (check/match)."""
        value = self.evaluate(node.value)
        
        for case in node.cases:
            match_result, bindings = self._match_pattern(case.pattern, value)
            
            if match_result:
                # Check guard if present
                if case.guard:
                    env = self.current_env.child("check")
                    for name, val in bindings.items():
                        env.define(name, val, mutable=False)
                    
                    prev_env = self.current_env
                    self.current_env = env
                    try:
                        guard_result = self.evaluate(case.guard)
                        if not self._is_truthy(guard_result):
                            continue
                    finally:
                        self.current_env = prev_env
                
                # Execute case body
                env = self.current_env.child("check")
                for name, val in bindings.items():
                    env.define(name, val, mutable=False)
                
                prev_env = self.current_env
                self.current_env = env
                try:
                    return self.evaluate(case.body)
                finally:
                    self.current_env = prev_env
        
        return None  # No match
    
    def _match_pattern(self, pattern: ast.Node, value: Any) -> tuple:
        """Match a pattern against a value. Returns (matched, bindings)."""
        bindings = {}
        
        if isinstance(pattern, ast.WildcardPattern):
            return True, bindings
        
        if isinstance(pattern, ast.Literal):
            return pattern.value == value, bindings
        
        if isinstance(pattern, ast.BindingPattern):
            bindings[pattern.name] = value
            return True, bindings
        
        if isinstance(pattern, ast.RangePattern):
            start = self.evaluate(pattern.start)
            end = self.evaluate(pattern.end)
            if isinstance(value, (int, float)):
                return start <= value <= end, bindings
            return False, bindings
        
        if isinstance(pattern, ast.ListLiteral):
            if not isinstance(value, list):
                return False, bindings
            if len(pattern.elements) != len(value):
                return False, bindings
            for p, v in zip(pattern.elements, value):
                matched, sub_bindings = self._match_pattern(p, v)
                if not matched:
                    return False, bindings
                bindings.update(sub_bindings)
            return True, bindings
        
        if isinstance(pattern, ast.MapLiteral):
            if not isinstance(value, dict):
                return False, bindings
            for key, pat in pattern.entries:
                key_val = self.evaluate(key) if key else None
                if key_val not in value:
                    return False, bindings
                matched, sub_bindings = self._match_pattern(pat, value[key_val])
                if not matched:
                    return False, bindings
                bindings.update(sub_bindings)
            return True, bindings
        
        # Try to evaluate the pattern as an expression
        try:
            pattern_val = self.evaluate(pattern)
            return pattern_val == value, bindings
        except Exception:
            return False, bindings
    
    def _eval_TryStatement(self, node: ast.TryStatement) -> Any:
        """Evaluate try/catch/finally."""
        result = None
        
        try:
            result = self.evaluate(node.try_block)
        except RiftError as e:
            if node.catch_block:
                env = self.current_env.child("catch")
                if node.catch_var:
                    env.define(node.catch_var, str(e), mutable=False)
                
                prev_env = self.current_env
                self.current_env = env
                try:
                    result = self.evaluate(node.catch_block)
                finally:
                    self.current_env = prev_env
        except Exception as e:
            # Don't catch control flow signals
            if isinstance(e, (BreakSignal, ContinueSignal, ReturnSignal, YieldSignal)):
                raise e
                
            if node.catch_block:
                env = self.current_env.child("catch")
                if node.catch_var:
                    env.define(node.catch_var, str(e), mutable=False)
                
                prev_env = self.current_env
                self.current_env = env
                try:
                    result = self.evaluate(node.catch_block)
                finally:
                    self.current_env = prev_env
        finally:
            if node.finally_block:
                self.evaluate(node.finally_block)
        
        return result
    
    def _eval_FailStatement(self, node: ast.FailStatement) -> None:
        """Throw an error."""
        error = self.evaluate(node.error)
        raise RuntimeError(str(error), node.line, node.column)
    
    def _eval_GiveStatement(self, node: ast.GiveStatement) -> None:
        """Return from function."""
        value = None
        if node.value:
            value = self.evaluate(node.value)
        raise ReturnSignal(value)
    
    def _eval_StopStatement(self, node: ast.StopStatement) -> None:
        """Break from loop."""
        raise BreakSignal()
    
    def _eval_NextStatement(self, node: ast.NextStatement) -> None:
        """Continue to next iteration."""
        raise ContinueSignal()
    
    def _eval_ClassDeclaration(self, node: ast.ClassDeclaration) -> RiftClass:
        """Define a class."""
        parent = None
        if node.parent:
            parent = self.current_env.get(node.parent)
            if not isinstance(parent, RiftClass):
                raise TypeError(f"Cannot extend non-class '{node.parent}'")
        
        methods = {}
        properties = {}
        static_methods = {}
        static_properties = {}
        constructor = None
        
        for member in node.body:
            if isinstance(member, ast.Constructor):
                constructor = member
            elif isinstance(member, ast.MethodDeclaration):
                func = RiftFunction(
                    ast.FunctionDeclaration(
                        name=member.name,
                        params=member.params,
                        body=member.body,
                        async_=member.async_,
                        line=member.line,
                        column=member.column
                    ),
                    self.current_env,
                    is_method=True
                )
                if member.static:
                    static_methods[member.name] = func
                else:
                    methods[member.name] = func
            elif isinstance(member, ast.PropertyDeclaration):
                value = None
                if member.value:
                    value = self.evaluate(member.value)
                if member.static:
                    static_properties[member.name] = value
                else:
                    properties[member.name] = value
        
        rift_class = RiftClass(
            name=node.name,
            methods=methods,
            properties=properties,
            parent=parent,
            static_methods=static_methods,
            static_properties=static_properties
        )
        
        # Store constructor separately
        if constructor:
            rift_class._constructor = constructor
        
        self.current_env.define(node.name, rift_class, mutable=False)
        return rift_class
    
    def _eval_ImportStatement(self, node: ast.ImportStatement) -> None:
        """Handle module imports."""
        module_name = node.module
        
        # Check if module is already loaded
        if module_name in self.modules:
            module = self.modules[module_name]
        else:
            module = self._load_module(module_name)
            self.modules[module_name] = module
        
        if node.wildcard:
            # Import all exports
            for name, value in module.items():
                self.current_env.define(name, value, mutable=False)
        elif node.items:
            # Import specific items
            for item in node.items:
                if item in module:
                    self.current_env.define(item, module[item], mutable=False)
                else:
                    raise RuntimeError(f"Module '{module_name}' has no export '{item}'")
        else:
            # Import module as namespace
            alias = node.alias or module_name.split('.')[-1]
            self.current_env.define(alias, module, mutable=False)
    
    def _load_module(self, name: str) -> Dict[str, Any]:
        """Load a module by name."""
        # Standard library modules
        stdlib = {
            'http': self._load_http_module,
            'db': self._load_db_module,
            'crypto': self._load_crypto_module,
            'fs': self._load_fs_module,
            'json': self._load_json_module,
            'websocket': self._load_websocket_module,
            'template': self._load_template_module,
            'ws': self._load_websocket_module,  # Alias
            'tpl': self._load_template_module,  # Alias
        }
        
        if name in stdlib:
            return stdlib[name]()
        
        # Try to load from file
        # For now, just return empty module
        return {}

        return {}
    
    def _load_http_module(self) -> Dict[str, Any]:
        """Load HTTP module."""
        from .stdlib.http import create_http_module
        return create_http_module(self)
    
    def _load_db_module(self) -> Dict[str, Any]:
        """Load database module."""
        from .stdlib.db import create_db_module
        return create_db_module(self)
    
    def _load_crypto_module(self) -> Dict[str, Any]:
        """Load crypto module."""
        from .stdlib.crypto import create_crypto_module
        return create_crypto_module(self)
    
    def _load_fs_module(self) -> Dict[str, Any]:
        """Load file system module."""
        from .stdlib.fs import create_fs_module
        return create_fs_module(self)
    
    def _load_json_module(self) -> Dict[str, Any]:
        """Load JSON module."""
        from .stdlib.json_lib import create_json_module
        return create_json_module(self)
    
    def _load_websocket_module(self) -> Dict[str, Any]:
        """Load WebSocket module."""
        from .stdlib.websocket import create_websocket_module
        return create_websocket_module(self)
    
    def _load_template_module(self) -> Dict[str, Any]:
        """Load Template module."""
        from .stdlib.template import create_template_module
        return create_template_module(self)
    
    def _eval_ExportStatement(self, node: ast.ExportStatement) -> None:
        """Handle exports (for module system)."""
        # Exports are handled during module loading
        if node.declaration:
            self.evaluate(node.declaration)
    
    # ========================================================================
    # Expressions
    # ========================================================================
    
    def _eval_Literal(self, node: ast.Literal) -> Any:
        return node.value
    
    def _eval_Identifier(self, node: ast.Identifier) -> Any:
        try:
            return self.current_env.get(node.name)
        except NameError:
            raise NameError(f"Undefined variable '{node.name}'", node.line, node.column)
    
    def _eval_BinaryOp(self, node: ast.BinaryOp) -> Any:
        """Evaluate binary operation."""
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        op = node.operator
        
        try:
            if op == '+':
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                if isinstance(left, list) and isinstance(right, list):
                    return left + right
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                if isinstance(left, str) and isinstance(right, int):
                    return left * right
                if isinstance(left, list) and isinstance(right, int):
                    return left * right
                return left * right
            elif op == '/':
                if right == 0:
                    raise DivisionByZeroError("Division by zero")
                return left / right
            elif op == '%':
                return left % right
            elif op == '**':
                return left ** right
            elif op == '==':
                return left == right
            elif op == '!=':
                return left != right
            elif op == '<':
                return left < right
            elif op == '>':
                return left > right
            elif op == '<=':
                return left <= right
            elif op == '>=':
                return left >= right
            elif op == 'in':
                return left in right
            else:
                raise RuntimeError(f"Unknown operator: {op}")
        except TypeError as e:
            raise TypeError(str(e), node.line, node.column)
    
    def _eval_UnaryOp(self, node: ast.UnaryOp) -> Any:
        """Evaluate unary operation."""
        operand = self.evaluate(node.operand)
        op = node.operator
        
        if op == '-':
            return -operand
        elif op == '+':
            return +operand
        elif op == 'not':
            return not self._is_truthy(operand)
        else:
            raise RuntimeError(f"Unknown unary operator: {op}")
    
    def _eval_Comparison(self, node: ast.Comparison) -> bool:
        """Evaluate comparison chain: a < b < c."""
        result = True
        
        for i, op in enumerate(node.operators):
            left = self.evaluate(node.operands[i])
            right = self.evaluate(node.operands[i + 1])
            
            if op == '<':
                result = result and (left < right)
            elif op == '>':
                result = result and (left > right)
            elif op == '<=':
                result = result and (left <= right)
            elif op == '>=':
                result = result and (left >= right)
            elif op == 'in':
                result = result and (left in right)
            
            if not result:
                return False
        
        return result
    
    def _eval_LogicalOp(self, node: ast.LogicalOp) -> Any:
        """Evaluate logical operation (short-circuit)."""
        left = self.evaluate(node.left)
        
        if node.operator == 'and':
            if not self._is_truthy(left):
                return left
            return self.evaluate(node.right)
        elif node.operator == 'or':
            if self._is_truthy(left):
                return left
            return self.evaluate(node.right)
    
    def _eval_Assignment(self, node: ast.Assignment) -> Any:
        """Evaluate assignment."""
        value = self.evaluate(node.value)
        
        # Compound assignment
        if node.operator != '=':
            old_value = self.evaluate(node.target)
            if node.operator == '+=':
                value = old_value + value
            elif node.operator == '-=':
                value = old_value - value
            elif node.operator == '*=':
                value = old_value * value
            elif node.operator == '/=':
                value = old_value / value
        
        # Assign to target
        if isinstance(node.target, ast.Identifier):
            try:
                self.current_env.set(node.target.name, value)
            except NameError:
                raise NameError(
                    f"Undefined variable '{node.target.name}'",
                    node.line, node.column
                )
            except AssignmentError as e:
                raise AssignmentError(str(e), node.line, node.column)
        elif isinstance(node.target, ast.MemberAccess):
            obj = self.evaluate(node.target.object)
            if isinstance(obj, RiftInstance):
                obj.set_property(node.target.property, value)
            elif isinstance(obj, dict):
                obj[node.target.property] = value
            else:
                raise TypeError(f"Cannot set property on {type_name(obj)}")
        elif isinstance(node.target, ast.IndexAccess):
            obj = self.evaluate(node.target.object)
            index = self.evaluate(node.target.index)
            if isinstance(obj, (list, dict)):
                obj[index] = value
            else:
                raise TypeError(f"Cannot index {type_name(obj)}")
        else:
            raise RuntimeError("Invalid assignment target")
        
        return value
    
    def _eval_Call(self, node: ast.Call) -> Any:
        """Evaluate function call."""
        callee = self.evaluate(node.callee)
        args = [self.evaluate(arg) for arg in node.arguments]
        
        # Flatten spread arguments
        flat_args = []
        for i, arg in enumerate(node.arguments):
            if isinstance(arg, ast.SpreadElement):
                if hasattr(args[i], '__iter__') and not isinstance(args[i], str):
                    flat_args.extend(args[i])
                else:
                    flat_args.append(args[i])
            else:
                flat_args.append(args[i])
        args = flat_args
        
        return self._call(callee, args, node)
    
    def _call(self, callee: Any, args: List[Any], node: ast.Node) -> Any:
        """Call a callable value."""
        # Built-in Python function
        if callable(callee) and not isinstance(callee, (RiftFunction, RiftLambda, RiftBoundMethod, RiftClass)):
            try:
                return callee(*args)
            except TypeError as e:
                raise ArgumentError(str(e), node.line, node.column)
        
        # RIFT function
        if isinstance(callee, RiftFunction):
            return self._call_function(callee, args, node)
        
        # RIFT lambda
        if isinstance(callee, RiftLambda):
            return self._call_lambda(callee, args, node)
        
        # Bound method
        if isinstance(callee, RiftBoundMethod):
            return self._call_bound_method(callee, args, node)
        
        # Class instantiation
        if isinstance(callee, RiftClass):
            return self._instantiate_class(callee, args, node)
        
        # Dict as namespace
        if isinstance(callee, dict):
            raise TypeError(
                f"Cannot call dict directly, use 'namespace.function()'",
                node.line, node.column
            )
        
        raise TypeError(
            f"Cannot call {type_name(callee)}",
            node.line, node.column
        )
    
    def _call_function(self, func: RiftFunction, args: List[Any], 
                       node: ast.Node) -> Any:
        """Call a RIFT function."""
        decl = func.declaration
        env = func.closure.child(decl.name)
        
        # Bind parameters
        params = decl.params
        for i, param in enumerate(params):
            if param.rest:
                # Rest parameter gets remaining arguments
                env.define(param.name, args[i:], mutable=False)
                break
            elif i < len(args):
                env.define(param.name, args[i], mutable=False)
            elif param.default:
                default_val = self.evaluate(param.default)
                env.define(param.name, default_val, mutable=False)
            else:
                env.define(param.name, None, mutable=False)
        
        # Execute function body
        prev_env = self.current_env
        self.current_env = env
        
        try:
            result = self.evaluate(decl.body)
            # Auto-return: last expression in block
            if isinstance(decl.body, ast.Block) and decl.body.statements:
                last = decl.body.statements[-1]
                if isinstance(last, ast.ExpressionStatement):
                    result = self.evaluate(last.expression)
            return result
        except ReturnSignal as ret:
            return ret.value
        finally:
            self.current_env = prev_env
    
    def _call_lambda(self, lamb: RiftLambda, args: List[Any],
                     node: ast.Node) -> Any:
        """Call a RIFT lambda."""
        env = lamb.closure.child("lambda")
        
        # Bind parameters
        for i, param in enumerate(lamb.node.params):
            if param.rest:
                env.define(param.name, args[i:], mutable=False)
                break
            elif i < len(args):
                env.define(param.name, args[i], mutable=False)
            elif param.default:
                prev_env = self.current_env
                self.current_env = env
                try:
                    default_val = self.evaluate(param.default)
                finally:
                    self.current_env = prev_env
                env.define(param.name, default_val, mutable=False)
            else:
                env.define(param.name, None, mutable=False)
        
        # Execute lambda body
        prev_env = self.current_env
        self.current_env = env
        
        try:
            return self.evaluate(lamb.node.body)
        except ReturnSignal as ret:
            return ret.value
        finally:
            self.current_env = prev_env
    
    def _call_bound_method(self, bound: RiftBoundMethod, args: List[Any],
                           node: ast.Node) -> Any:
        """Call a bound method."""
        func = bound.method
        decl = func.declaration
        env = func.closure.child(decl.name)
        
        # Bind 'me' to instance
        env.define('me', bound.instance, mutable=False)
        
        # Bind parameters
        for i, param in enumerate(decl.params):
            if param.rest:
                env.define(param.name, args[i:], mutable=False)
                break
            elif i < len(args):
                env.define(param.name, args[i], mutable=False)
            elif param.default:
                default_val = self.evaluate(param.default)
                env.define(param.name, default_val, mutable=False)
            else:
                env.define(param.name, None, mutable=False)
        
        prev_env = self.current_env
        self.current_env = env
        
        try:
            result = self.evaluate(decl.body)
            return result
        except ReturnSignal as ret:
            return ret.value
        finally:
            self.current_env = prev_env
    
    def _instantiate_class(self, cls: RiftClass, args: List[Any],
                           node: ast.Node) -> RiftInstance:
        """Create an instance of a class."""
        instance = RiftInstance(cls)
        
        # Call constructor if defined
        if hasattr(cls, '_constructor') and cls._constructor:
            constructor = cls._constructor
            env = self.current_env.child("build")
            env.define('me', instance, mutable=False)
            
            # Bind constructor parameters
            for i, param in enumerate(constructor.params):
                if i < len(args):
                    env.define(param.name, args[i], mutable=False)
                elif param.default:
                    default_val = self.evaluate(param.default)
                    env.define(param.name, default_val, mutable=False)
                else:
                    env.define(param.name, None, mutable=False)
            
            prev_env = self.current_env
            self.current_env = env
            
            try:
                self.evaluate(constructor.body)
            except ReturnSignal:
                pass  # Ignore returns in constructor
            finally:
                self.current_env = prev_env
        
        return instance
    
    def _eval_MemberAccess(self, node: ast.MemberAccess) -> Any:
        """Evaluate member access: obj.prop or obj?.prop."""
        obj = self.evaluate(node.object)
        
        # Safe navigation
        if node.safe and obj is None:
            return None
        
        if obj is None:
            raise TypeError(f"Cannot access property '{node.property}' of none")
        
        # RIFT instance
        if isinstance(obj, RiftInstance):
            try:
                # Try property first
                return obj.get_property(node.property)
            except AttributeError:
                # Try method
                try:
                    method = obj.get_method(node.property)
                    return RiftBoundMethod(obj, method)
                except AttributeError:
                    raise NameError(f"'{obj._class.name}' has no property or method '{node.property}'")
        
        # RIFT class (static access)
        if isinstance(obj, RiftClass):
            if node.property in obj.static_properties:
                return obj.static_properties[node.property]
            if node.property in obj.static_methods:
                return obj.static_methods[node.property]
            raise NameError(f"Class '{obj.name}' has no static member '{node.property}'")
        
        # Dict
        if isinstance(obj, dict):
            if node.property in obj:
                return obj[node.property]
            if node.safe:
                return None
            raise NameError(f"Key '{node.property}' not found in map")
        
        # String methods
        if isinstance(obj, str):
            return self._get_string_method(obj, node.property)
        
        # List methods
        if isinstance(obj, list):
            return self._get_list_method(obj, node.property)
        
        # Try attribute
        if hasattr(obj, node.property):
            return getattr(obj, node.property)
        
        raise TypeError(f"Cannot access property '{node.property}' of {type_name(obj)}")
    
    def _get_string_method(self, s: str, method: str) -> Any:
        """Get method on string."""
        methods = {
            'length': len(s),
            'upper': s.upper,
            'lower': s.lower,
            'trim': s.strip,
            'split': s.split,
            'replace': s.replace,
            'startsWith': s.startswith,
            'endsWith': s.endswith,
            'includes': lambda x: x in s,
            'indexOf': s.find,
            'charAt': lambda i: s[i] if 0 <= i < len(s) else '',
            'substring': lambda start, end=None: s[start:end],
            'repeat': lambda n: s * n,
            'padStart': lambda n, c=' ': s.rjust(n, c),
            'padEnd': lambda n, c=' ': s.ljust(n, c),
        }
        
        if method in methods:
            return methods[method]
        
        raise NameError(f"String has no method '{method}'")
    
    def _get_list_method(self, lst: list, method: str) -> Any:
        """Get method on list."""
        methods = {
            'length': len(lst),
            'push': lst.append,
            'pop': lst.pop,
            'shift': lambda: lst.pop(0) if lst else None,
            'unshift': lambda x: lst.insert(0, x),
            'slice': lambda start=0, end=None: lst[start:end],
            'indexOf': lambda x: lst.index(x) if x in lst else -1,
            'includes': lambda x: x in lst,
            'join': lambda sep='': sep.join(str(x) for x in lst),
            'reverse': lambda: list(reversed(lst)),
            'sort': lambda: sorted(lst),
            'concat': lambda other: lst + other,
            'flat': lambda: [item for sublist in lst for item in (sublist if isinstance(sublist, list) else [sublist])],
            'fill': lambda val: [val] * len(lst),
        }
        
        if method in methods:
            return methods[method]
        
        raise NameError(f"List has no method '{method}'")
    
    def _eval_IndexAccess(self, node: ast.IndexAccess) -> Any:
        """Evaluate index access: arr[i] or arr?[i]."""
        obj = self.evaluate(node.object)
        
        if node.safe and obj is None:
            return None
        
        if obj is None:
            raise TypeError("Cannot index none")
        
        index = self.evaluate(node.index)
        
        try:
            if isinstance(obj, (list, str)):
                if isinstance(index, int):
                    if node.safe and (index < 0 or index >= len(obj)):
                        return None
                    return obj[index]
            if isinstance(obj, dict):
                if node.safe and index not in obj:
                    return None
                return obj[index]
            return obj[index]
        except (IndexError, KeyError):
            if node.safe:
                return None
            raise
    
    def _eval_StaticAccess(self, node: ast.StaticAccess) -> Any:
        """Evaluate static access: Class::method."""
        obj = self.evaluate(node.object)
        
        if isinstance(obj, RiftClass):
            if node.property in obj.static_methods:
                return obj.static_methods[node.property]
            if node.property in obj.static_properties:
                return obj.static_properties[node.property]
            raise NameError(f"Class '{obj.name}' has no static member '{node.property}'")
        
        if isinstance(obj, dict):
            return obj.get(node.property)
        
        raise TypeError(f"Cannot use :: on {type_name(obj)}")
    
    def _eval_ListLiteral(self, node: ast.ListLiteral) -> list:
        """Evaluate list literal."""
        result = []
        for elem in node.elements:
            if isinstance(elem, ast.SpreadElement):
                val = self.evaluate(elem.argument)
                if hasattr(val, '__iter__') and not isinstance(val, str):
                    result.extend(val)
                else:
                    result.append(val)
            else:
                result.append(self.evaluate(elem))
        return result
    
    def _eval_MapLiteral(self, node: ast.MapLiteral) -> dict:
        """Evaluate map literal."""
        result = {}
        for key, value in node.entries:
            if key is None and isinstance(value, ast.SpreadElement):
                # Spread in map
                spread_val = self.evaluate(value.argument)
                if isinstance(spread_val, dict):
                    result.update(spread_val)
            else:
                key_val = self.evaluate(key)
                val = self.evaluate(value)
                result[key_val] = val
        return result
    
    def _eval_Range(self, node: ast.Range) -> range:
        """Evaluate range expression."""
        start = self.evaluate(node.start)
        end = self.evaluate(node.end)
        
        if not isinstance(start, int) or not isinstance(end, int):
            raise TypeError("Range bounds must be integers")
        
        if node.inclusive:
            return range(start, end + 1)
        return range(start, end)
    
    def _eval_Pipeline(self, node: ast.Pipeline) -> Any:
        """Evaluate pipeline: value -> transform1 -> transform2.
        
        The pipeline operator treats stages in two ways:
        1. If the stage is an identifier like `sum`, look up the function and call with value as argument
        2. If the stage is a call like `method(args)` where method is an identifier, 
           try to call it as a method on the value: value.method(args)
           If not a method, append value as the last argument: method(args, value)
        """
        value = self.evaluate(node.value)
        
        for stage in node.stages:
            if isinstance(stage, ast.Call):
                # Check if callee is a simple identifier - if so, try method call on value first
                if isinstance(stage.callee, ast.Identifier):
                    method_name = stage.callee.name
                    args = [self.evaluate(arg) for arg in stage.arguments]
                    
                    # Try as method on value first
                    method = self._try_get_method(value, method_name)
                    if method is not None:
                        value = self._call(method, args, stage)
                    else:
                        # Fall back to function call with value as LAST arg
                        # This matches the pattern: filter(pred, list), map(fn, list)
                        try:
                            func = self.evaluate(stage.callee)
                            value = self._call(func, args + [value], stage)
                        except NameError:
                            raise NameError(f"'{method_name}' is not a method of {type_name(value)} or a defined function")
                else:
                    # Callee is an expression - evaluate it and call with value as last arg
                    callee = self.evaluate(stage.callee)
                    args = [self.evaluate(arg) for arg in stage.arguments] + [value]
                    value = self._call(callee, args, stage)
            elif isinstance(stage, ast.Lambda):
                # Apply lambda to value
                lamb = RiftLambda(stage, self.current_env)
                value = self._call_lambda(lamb, [value], stage)
            elif isinstance(stage, ast.Identifier):
                # Try as method on value first, then as function
                method = self._try_get_method(value, stage.name)
                if method is not None:
                    value = self._call(method, [], stage)
                else:
                    func = self.evaluate(stage)
                    value = self._call(func, [value], stage)
            else:
                # Evaluate stage and try to call it
                func = self.evaluate(stage)
                value = self._call(func, [value], stage)
        
        return value
    
    def _try_get_method(self, obj: Any, method_name: str) -> Any:
        """Try to get a method from an object, returning None if not found."""
        try:
            if hasattr(obj, method_name):
                attr = getattr(obj, method_name)
                if callable(attr):
                    return attr
            if isinstance(obj, dict) and method_name in obj and callable(obj[method_name]):
                return obj[method_name]
        except Exception:
            pass
        return None
    
    def _eval_Lambda(self, node: ast.Lambda) -> RiftLambda:
        """Evaluate lambda expression."""
        return RiftLambda(node, self.current_env)
    
    def _eval_Ternary(self, node: ast.Ternary) -> Any:
        """Evaluate ternary expression."""
        condition = self.evaluate(node.condition)
        if self._is_truthy(condition):
            return self.evaluate(node.then_expr)
        return self.evaluate(node.else_expr)
    
    def _eval_NullCoalesce(self, node: ast.NullCoalesce) -> Any:
        """Evaluate null coalescing: value ?? default."""
        left = self.evaluate(node.left)
        if left is None:
            return self.evaluate(node.right)
        return left
    
    def _eval_SpreadElement(self, node: ast.SpreadElement) -> Any:
        """Evaluate spread element."""
        return self.evaluate(node.argument)
    
    def _eval_Await(self, node: ast.Await) -> Any:
        """Evaluate await expression."""
        value = self.evaluate(node.expression)
        
        if asyncio.iscoroutine(value):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(value)
        
        return value
    
    def _eval_Yield(self, node: ast.Yield) -> None:
        """Evaluate yield expression."""
        value = None
        if node.expression:
            value = self.evaluate(node.expression)
        raise YieldSignal(value)
    
    def _eval_TemplateString(self, node: ast.TemplateString) -> str:
        """Evaluate template string with interpolation."""
        parts = []
        for part in node.parts:
            if isinstance(part, ast.Literal) and isinstance(part.value, str):
                parts.append(part.value)
            else:
                val = self.evaluate(part)
                parts.append(str(val) if val is not None else 'none')
        return ''.join(parts)
    
    def _eval_Me(self, node: ast.Me) -> Any:
        """Evaluate 'me' reference."""
        try:
            return self.current_env.get('me')
        except NameError:
            raise NameError("'me' can only be used inside a class method", node.line, node.column)
    
    def _eval_Parent(self, node: ast.Parent) -> Any:
        """Evaluate 'parent' reference."""
        try:
            me = self.current_env.get('me')
            if isinstance(me, RiftInstance) and me._class.parent:
                # Return parent class for method lookup
                return me._class.parent
            raise NameError("No parent class")
        except NameError:
            raise NameError("'parent' can only be used inside a class method", node.line, node.column)
    
    # ========================================================================
    # Helpers
    # ========================================================================
    
    def _is_truthy(self, value: Any) -> bool:
        """Determine if a value is truthy."""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        if isinstance(value, (list, dict)):
            return len(value) > 0
        return True
    
    # ========================================================================
    # Built-in Functions
    # ========================================================================
    
    def _builtin_print(self, *args):
        """Print to console."""
        output = ' '.join(str(arg) if arg is not None else 'none' for arg in args)
        print(output)
        return None
    
    def _builtin_input(self, prompt=''):
        """Read from stdin."""
        return input(prompt)
    
    def _builtin_len(self, obj):
        """Get length of collection."""
        if obj is None:
            return 0
        return len(obj)
    
    def _builtin_type(self, value):
        """Get type of value."""
        return type_name(value)
    
    def _builtin_range(self, start, end=None, step=1):
        """Generate range."""
        if end is None:
            return list(range(int(start)))
        return list(range(int(start), int(end), int(step)))
    
    def _builtin_map(self, func, iterable):
        """Map function over iterable."""
        result = []
        for item in iterable:
            result.append(self._call(func, [item], None))
        return result
    
    def _builtin_filter(self, func, iterable):
        """Filter iterable by function."""
        result = []
        for item in iterable:
            if self._is_truthy(self._call(func, [item], None)):
                result.append(item)
        return result
    
    def _builtin_reduce(self, func, iterable, initial=None):
        """Reduce iterable with function."""
        it = iter(iterable)
        if initial is None:
            try:
                acc = next(it)
            except StopIteration:
                raise ArgumentError("reduce() of empty sequence with no initial value")
        else:
            acc = initial
        
        for item in it:
            acc = self._call(func, [acc, item], None)
        return acc
    
    def _builtin_sort(self, iterable, key=None, reverse=False):
        """Sort iterable."""
        if key:
            return sorted(iterable, key=lambda x: self._call(key, [x], None), reverse=reverse)
        return sorted(iterable, reverse=reverse)
    
    def _builtin_reverse(self, iterable):
        """Reverse iterable."""
        if isinstance(iterable, str):
            return iterable[::-1]
        return list(reversed(iterable))
    
    def _builtin_keys(self, obj):
        """Get keys of map."""
        if isinstance(obj, dict):
            return list(obj.keys())
        raise TypeError("keys() requires a map")
    
    def _builtin_values(self, obj):
        """Get values of map."""
        if isinstance(obj, dict):
            return list(obj.values())
        raise TypeError("values() requires a map")
    
    def _builtin_entries(self, obj):
        """Get entries of map."""
        if isinstance(obj, dict):
            return [[k, v] for k, v in obj.items()]
        raise TypeError("entries() requires a map")
    
    def _builtin_split(self, s, sep=None):
        """Split string."""
        return s.split(sep)
    
    def _builtin_join(self, iterable, sep=''):
        """Join iterable."""
        return sep.join(str(x) for x in iterable)
    
    def _builtin_now(self):
        """Get current timestamp."""
        import time
        return time.time()
    
    async def _async_sleep(self, seconds):
        """Async sleep helper."""
        await asyncio.sleep(seconds)
    
    def _builtin_sleep(self, seconds):
        """Sleep for seconds."""
        import time
        time.sleep(seconds)
    
    def _builtin_str(self, value):
        """Convert to string."""
        if value is None:
            return 'none'
        return str(value)
    
    def _builtin_num(self, value):
        """Convert to number."""
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
    
    def _builtin_int(self, value):
        """Convert to integer."""
        return int(self._builtin_num(value))
    
    def _builtin_float(self, value):
        """Convert to float."""
        return float(self._builtin_num(value))
    
    def _builtin_bool(self, value):
        """Convert to boolean."""
        return self._is_truthy(value)
    
    def _builtin_list(self, value):
        """Convert to list."""
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return list(value)
        if isinstance(value, dict):
            return list(value.items())
        if hasattr(value, '__iter__'):
            return list(value)
        return [value]
    
    def _builtin_sum(self, iterable):
        """Sum of iterable."""
        return sum(iterable)
    
    def _builtin_min(self, *args):
        """Minimum value."""
        if len(args) == 1 and hasattr(args[0], '__iter__'):
            return min(args[0])
        return min(args)
    
    def _builtin_max(self, *args):
        """Maximum value."""
        if len(args) == 1 and hasattr(args[0], '__iter__'):
            return max(args[0])
        return max(args)
    
    def _builtin_abs(self, value):
        """Absolute value."""
        return abs(value)
    
    def _builtin_round(self, value, digits=0):
        """Round number."""
        return round(value, digits)
    
    def _builtin_floor(self, value):
        """Floor of number."""
        import math
        return math.floor(value)
    
    def _builtin_ceil(self, value):
        """Ceiling of number."""
        import math
        return math.ceil(value)
    
    def _builtin_push(self, lst, value):
        """Append to list."""
        lst.append(value)
        return lst
    
    def _builtin_pop(self, lst):
        """Pop from list."""
        return lst.pop() if lst else None
    
    def _builtin_shift(self, lst):
        """Remove first element."""
        return lst.pop(0) if lst else None
    
    def _builtin_unshift(self, lst, value):
        """Add to beginning of list."""
        lst.insert(0, value)
        return lst
    
    def _builtin_slice(self, obj, start=0, end=None):
        """Slice list or string."""
        return obj[start:end]
    
    def _builtin_index_of(self, obj, value):
        """Find index of value."""
        try:
            return obj.index(value)
        except ValueError:
            return -1
    
    def _builtin_includes(self, obj, value):
        """Check if value is in collection."""
        return value in obj
    
    def _builtin_find(self, lst, func):
        """Find first matching element."""
        for item in lst:
            if self._is_truthy(self._call(func, [item], None)):
                return item
        return None
    
    def _builtin_every(self, lst, func):
        """Check if all elements match."""
        for item in lst:
            if not self._is_truthy(self._call(func, [item], None)):
                return False
        return True
    
    def _builtin_some(self, lst, func):
        """Check if any element matches."""
        for item in lst:
            if self._is_truthy(self._call(func, [item], None)):
                return True
        return False
    
    def _builtin_concat(self, *args):
        """Concatenate lists."""
        result = []
        for arg in args:
            if isinstance(arg, list):
                result.extend(arg)
            else:
                result.append(arg)
        return result
    
    def _builtin_flat(self, lst, depth=1):
        """Flatten list."""
        result = []
        for item in lst:
            if isinstance(item, list) and depth > 0:
                result.extend(self._builtin_flat(item, depth - 1))
            else:
                result.append(item)
        return result
    
    def _builtin_fill(self, lst, value, start=0, end=None):
        """Fill list with value."""
        if end is None:
            end = len(lst)
        for i in range(start, end):
            if i < len(lst):
                lst[i] = value
        return lst
    
    def _builtin_upper(self, s):
        """Convert to uppercase."""
        return s.upper()
    
    def _builtin_lower(self, s):
        """Convert to lowercase."""
        return s.lower()
    
    def _builtin_trim(self, s):
        """Trim whitespace."""
        return s.strip()
    
    def _builtin_replace(self, s, old, new):
        """Replace in string."""
        return s.replace(old, new)
    
    def _builtin_starts_with(self, s, prefix):
        """Check if string starts with prefix."""
        return s.startswith(prefix)
    
    def _builtin_ends_with(self, s, suffix):
        """Check if string ends with suffix."""
        return s.endswith(suffix)
    
    def _builtin_char_at(self, s, index):
        """Get character at index."""
        if 0 <= index < len(s):
            return s[index]
        return ''
    
    def _builtin_substring(self, s, start, end=None):
        """Get substring."""
        return s[start:end]
    
    def _builtin_repeat_str(self, s, n):
        """Repeat string."""
        return s * n
    
    def _builtin_pad_start(self, s, length, fill=' '):
        """Pad string at start."""
        return s.rjust(length, fill)
    
    def _builtin_pad_end(self, s, length, fill=' '):
        """Pad string at end."""
        return s.ljust(length, fill)


def interpret(source: str, filename: str = "<stdin>") -> Any:
    """Convenience function to interpret source code."""
    from .parser import parse
    program = parse(source, filename)
    interpreter = Interpreter()
    return interpreter.execute(program)
