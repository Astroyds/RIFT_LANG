"""
RIFT Language Parser

Parses tokens into an Abstract Syntax Tree (AST).
Implements recursive descent parsing with operator precedence.
"""

from typing import List, Optional, Any, Callable
from .lexer import Token, TokenType, tokenize
from .errors import ParseError
from . import ast_nodes as ast


class Parser:
    """
    Recursive descent parser for the RIFT language.
    
    Operator Precedence (lowest to highest):
    1. Assignment: = += -= *= /=
    2. Pipeline: -> <- ~>
    3. Null coalesce: ??
    4. Logical or: or
    5. Logical and: and
    6. Equality: == !=
    7. Comparison: < > <= >= in
    8. Range: .. to
    9. Addition: + -
    10. Multiplication: * / %
    11. Power: **
    12. Unary: not - +
    13. Call/Access: () [] . ?. ?[ ::
    """
    
    def __init__(self, tokens: List[Token], filename: str = "<stdin>"):
        self.tokens = tokens
        self.filename = filename
        self.pos = 0
    
    @property
    def current(self) -> Token:
        """Get current token."""
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # Return EOF
        return self.tokens[self.pos]
    
    def peek(self, offset: int = 1) -> Token:
        """Look ahead by offset tokens."""
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[pos]
    
    def is_at_end(self) -> bool:
        """Check if we've reached the end."""
        return self.current.type == TokenType.EOF
    
    def error(self, message: str, token: Optional[Token] = None) -> ParseError:
        """Create a parse error."""
        token = token or self.current
        return ParseError(message, token.line, token.column, self.filename)
    
    def check(self, *types: TokenType) -> bool:
        """Check if current token is one of the given types."""
        return self.current.type in types
    
    def match(self, *types: TokenType) -> bool:
        """If current token matches, advance and return True."""
        if self.check(*types):
            self.advance()
            return True
        return False
    
    def advance(self) -> Token:
        """Consume and return current token."""
        token = self.current
        if not self.is_at_end():
            self.pos += 1
        return token
    
    def expect(self, type: TokenType, message: str = None) -> Token:
        """Consume token of expected type or raise error."""
        if self.check(type):
            return self.advance()
        msg = message or f"Expected {type.name}, got {self.current.type.name}"
        raise self.error(msg)
    
    def skip_newlines(self):
        """Skip any newline tokens."""
        while self.check(TokenType.NEWLINE):
            self.advance()
    
    def is_statement_end(self) -> bool:
        """Check if we're at a statement boundary."""
        return self.check(TokenType.NEWLINE, TokenType.SEMICOLON, TokenType.EOF,
                          TokenType.RBRACE)
    
    def consume_statement_end(self):
        """Consume statement terminators."""
        while self.check(TokenType.NEWLINE, TokenType.SEMICOLON):
            self.advance()
    
    # ========================================================================
    # Entry Point
    # ========================================================================
    
    def parse(self) -> ast.Program:
        """Parse the entire program."""
        program = ast.Program(body=[], line=1, column=1)
        self.skip_newlines()
        
        while not self.is_at_end():
            stmt = self.parse_statement()
            if stmt:
                program.body.append(stmt)
            self.skip_newlines()
        
        return program
    
    # ========================================================================
    # Statements
    # ========================================================================
    
    def parse_statement(self) -> ast.Node:
        """Parse a single statement."""
        self.skip_newlines()
        
        # Variable declarations
        if self.check(TokenType.LET, TokenType.MUT, TokenType.CONST):
            return self.parse_variable_declaration()
        
        # Function declaration
        if self.check(TokenType.CONDUIT):
            return self.parse_function_declaration()
        
        # Async function
        if self.check(TokenType.ASYNC):
            return self.parse_async_declaration()
        
        # Class declaration
        if self.check(TokenType.MAKE):
            return self.parse_class_declaration()
        
        # Control flow
        if self.check(TokenType.IF):
            return self.parse_if_statement()
        
        if self.check(TokenType.WHILE):
            return self.parse_while_statement()
        
        if self.check(TokenType.REPEAT):
            return self.parse_repeat_statement()
        
        if self.check(TokenType.CHECK):
            return self.parse_check_statement()
        
        if self.check(TokenType.TRY):
            return self.parse_try_statement()
        
        # Control keywords
        if self.check(TokenType.GIVE):
            return self.parse_give_statement()
        
        if self.check(TokenType.FAIL):
            return self.parse_fail_statement()
        
        if self.check(TokenType.STOP):
            token = self.advance()
            self.consume_statement_end()
            return ast.StopStatement(line=token.line, column=token.column)
        
        if self.check(TokenType.NEXT):
            token = self.advance()
            self.consume_statement_end()
            return ast.NextStatement(line=token.line, column=token.column)
        
        # Module system
        if self.check(TokenType.GRAB):
            return self.parse_import_statement()
        
        if self.check(TokenType.SHARE):
            return self.parse_export_statement()
        
        # Expression statement
        return self.parse_expression_statement()
    
    def parse_variable_declaration(self) -> ast.Node:
        """Parse: let/mut/const name [: type] = value."""
        kind_token = self.advance()  # let, mut, or const
        kind = kind_token.value
        
        # Check for destructuring
        if self.check(TokenType.LBRACKET):
            return self.parse_list_destructuring(kind, kind_token)
        if self.check(TokenType.LBRACE):
            return self.parse_map_destructuring(kind, kind_token)
        
        name_token = self.expect(TokenType.IDENTIFIER, "Expected variable name")
        name = name_token.value
        
        # Optional type hint
        type_hint = None
        if self.match(TokenType.COLON):
            type_token = self.expect(TokenType.IDENTIFIER, "Expected type name")
            type_hint = type_token.value
        
        # Optional initializer
        value = None
        if self.match(TokenType.ASSIGN):
            value = self.parse_expression()
        
        self.consume_statement_end()
        
        return ast.VariableDeclaration(
            kind=kind,
            name=name,
            type_hint=type_hint,
            value=value,
            line=kind_token.line,
            column=kind_token.column
        )
    
    def parse_list_destructuring(self, kind: str, kind_token: Token) -> ast.DestructuringDeclaration:
        """Parse: let [a, b, ...rest] = value."""
        self.expect(TokenType.LBRACKET)
        elements = []
        
        while not self.check(TokenType.RBRACKET):
            if self.match(TokenType.SPREAD):
                name = self.expect(TokenType.IDENTIFIER).value
                elements.append(ast.SpreadElement(
                    argument=ast.Identifier(name=name),
                    line=self.current.line,
                    column=self.current.column
                ))
            else:
                name = self.expect(TokenType.IDENTIFIER).value
                elements.append(ast.Identifier(name=name))
            
            if not self.check(TokenType.RBRACKET):
                self.expect(TokenType.COMMA)
        
        self.expect(TokenType.RBRACKET)
        self.expect(TokenType.ASSIGN, "Expected '=' after destructuring pattern")
        value = self.parse_expression()
        self.consume_statement_end()
        
        pattern = ast.ListPattern(elements=elements)
        return ast.DestructuringDeclaration(
            kind=kind,
            pattern=pattern,
            value=value,
            line=kind_token.line,
            column=kind_token.column
        )
    
    def parse_map_destructuring(self, kind: str, kind_token: Token) -> ast.DestructuringDeclaration:
        """Parse: let {a, b: alias} = value."""
        self.expect(TokenType.LBRACE)
        entries = []
        
        while not self.check(TokenType.RBRACE):
            key = self.expect(TokenType.IDENTIFIER).value
            alias = key
            
            if self.match(TokenType.COLON):
                alias = self.expect(TokenType.IDENTIFIER).value
            
            entries.append((key, alias))
            
            if not self.check(TokenType.RBRACE):
                self.expect(TokenType.COMMA)
        
        self.expect(TokenType.RBRACE)
        self.expect(TokenType.ASSIGN, "Expected '=' after destructuring pattern")
        value = self.parse_expression()
        self.consume_statement_end()
        
        pattern = ast.MapPattern(entries=entries)
        return ast.DestructuringDeclaration(
            kind=kind,
            pattern=pattern,
            value=value,
            line=kind_token.line,
            column=kind_token.column
        )
    
    def parse_function_declaration(self, async_: bool = False) -> ast.FunctionDeclaration:
        """Parse: conduit name(params) { body }."""
        keyword = self.expect(TokenType.CONDUIT)
        
        # Check for generator
        generator = self.match(TokenType.STAR)
        
        name_token = self.expect(TokenType.IDENTIFIER, "Expected function name")
        
        params = self.parse_parameters()
        
        # Optional return type
        return_type = None
        if self.match(TokenType.COLON):
            return_type = self.expect(TokenType.IDENTIFIER).value
        
        body = self.parse_block()
        
        return ast.FunctionDeclaration(
            name=name_token.value,
            params=params,
            body=body,
            async_=async_,
            generator=generator,
            return_type=return_type,
            line=keyword.line,
            column=keyword.column
        )
    
    def parse_async_declaration(self) -> ast.FunctionDeclaration:
        """Parse: async conduit name(params) { body }."""
        self.expect(TokenType.ASYNC)
        return self.parse_function_declaration(async_=True)
    
    def parse_parameters(self) -> List[ast.Parameter]:
        """Parse function parameters."""
        self.expect(TokenType.LPAREN)
        params = []
        
        while not self.check(TokenType.RPAREN):
            # Check for rest parameter
            rest = self.match(TokenType.SPREAD)
            
            name_token = self.expect(TokenType.IDENTIFIER, "Expected parameter name")
            
            # Optional type hint
            type_hint = None
            if self.match(TokenType.COLON):
                type_hint = self.expect(TokenType.IDENTIFIER).value
            
            # Optional default value
            default = None
            if self.match(TokenType.ASSIGN):
                default = self.parse_expression()
            
            params.append(ast.Parameter(
                name=name_token.value,
                type_hint=type_hint,
                default=default,
                rest=rest,
                line=name_token.line,
                column=name_token.column
            ))
            
            if not self.check(TokenType.RPAREN):
                self.expect(TokenType.COMMA)
        
        self.expect(TokenType.RPAREN)
        return params
    
    def parse_block(self) -> ast.Block:
        """Parse: { statements }."""
        open_brace = self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        statements = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE, "Expected '}'")
        
        return ast.Block(
            statements=statements,
            line=open_brace.line,
            column=open_brace.column
        )
    
    def parse_class_declaration(self) -> ast.ClassDeclaration:
        """Parse: make ClassName [extend Parent] { body }."""
        keyword = self.expect(TokenType.MAKE)
        name = self.expect(TokenType.IDENTIFIER, "Expected class name").value
        
        # Optional parent class
        parent = None
        if self.match(TokenType.EXTEND):
            parent = self.expect(TokenType.IDENTIFIER, "Expected parent class name").value
        
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        body = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            member = self.parse_class_member()
            if member:
                body.append(member)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        
        return ast.ClassDeclaration(
            name=name,
            parent=parent,
            body=body,
            line=keyword.line,
            column=keyword.column
        )
    
    def parse_class_member(self) -> ast.Node:
        """Parse a class member (method, property, constructor)."""
        self.skip_newlines()
        
        is_static = self.match(TokenType.STATIC)
        is_async = self.match(TokenType.ASYNC)
        
        # Constructor
        if self.check(TokenType.BUILD):
            return self.parse_constructor()
        
        # Getter - check for identifier 'get' followed by another identifier
        if self.check(TokenType.IDENTIFIER) and self.current.value == 'get':
            next_tok = self.peek()
            if next_tok.type == TokenType.IDENTIFIER:
                self.advance()  # consume 'get'
                name = self.expect(TokenType.IDENTIFIER).value
                params = self.parse_parameters()
                body = self.parse_block()
                return ast.MethodDeclaration(
                    name=name,
                    params=params,
                    body=body,
                    static=is_static,
                    is_getter=True,
                    line=self.current.line,
                    column=self.current.column
                )
        
        # Setter - check for identifier 'set' followed by another identifier
        if self.check(TokenType.IDENTIFIER) and self.current.value == 'set':
            next_tok = self.peek()
            if next_tok.type == TokenType.IDENTIFIER:
                self.advance()  # consume 'set'
                name = self.expect(TokenType.IDENTIFIER).value
                params = self.parse_parameters()
                body = self.parse_block()
                return ast.MethodDeclaration(
                    name=name,
                    params=params,
                    body=body,
                    static=is_static,
                    is_setter=True,
                    line=self.current.line,
                    column=self.current.column
                )
        
        # Method or property
        if self.check(TokenType.CONDUIT):
            self.advance()
            name = self.expect(TokenType.IDENTIFIER).value
            params = self.parse_parameters()
            body = self.parse_block()
            return ast.MethodDeclaration(
                name=name,
                params=params,
                body=body,
                async_=is_async,
                static=is_static,
                line=self.current.line,
                column=self.current.column
            )
        
        # Property (identifier with optional type and value)
        if self.check(TokenType.IDENTIFIER):
            name = self.advance().value
            
            type_hint = None
            if self.match(TokenType.COLON):
                type_hint = self.expect(TokenType.IDENTIFIER).value
            
            value = None
            if self.match(TokenType.ASSIGN):
                value = self.parse_expression()
            
            self.consume_statement_end()
            
            return ast.PropertyDeclaration(
                name=name,
                type_hint=type_hint,
                value=value,
                static=is_static
            )
        
        raise self.error("Expected class member")
    
    def parse_constructor(self) -> ast.Constructor:
        """Parse: build(params) { body }."""
        keyword = self.expect(TokenType.BUILD)
        params = self.parse_parameters()
        body = self.parse_block()
        
        return ast.Constructor(
            params=params,
            body=body,
            line=keyword.line,
            column=keyword.column
        )
    
    def parse_if_statement(self) -> ast.IfStatement:
        """Parse: if condition { then } [else { else }]."""
        keyword = self.expect(TokenType.IF)
        condition = self.parse_expression()
        then_branch = self.parse_block()
        
        else_branch = None
        self.skip_newlines()
        if self.match(TokenType.ELSE):
            if self.check(TokenType.IF):
                else_branch = self.parse_if_statement()
            else:
                else_branch = self.parse_block()
        
        return ast.IfStatement(
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch,
            line=keyword.line,
            column=keyword.column
        )
    
    def parse_while_statement(self) -> ast.WhileStatement:
        """Parse: while condition { body }."""
        keyword = self.expect(TokenType.WHILE)
        condition = self.parse_expression()
        body = self.parse_block()
        
        return ast.WhileStatement(
            condition=condition,
            body=body,
            line=keyword.line,
            column=keyword.column
        )
    
    def parse_repeat_statement(self) -> ast.RepeatStatement:
        """Parse: repeat item in iterable { body } or repeat (i, item) in iterable."""
        keyword = self.expect(TokenType.REPEAT)
        
        index_var = None
        
        # Check for (index, item) pattern
        if self.match(TokenType.LPAREN):
            index_var = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.COMMA)
            variable = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.RPAREN)
        else:
            variable = self.expect(TokenType.IDENTIFIER).value
        
        self.expect(TokenType.IN, "Expected 'in' after loop variable")
        iterable = self.parse_expression()
        body = self.parse_block()
        
        return ast.RepeatStatement(
            variable=variable,
            index_var=index_var,
            iterable=iterable,
            body=body,
            line=keyword.line,
            column=keyword.column
        )
    
    def parse_check_statement(self) -> ast.CheckStatement:
        """Parse: check value { cases }."""
        keyword = self.expect(TokenType.CHECK)
        value = self.parse_expression()
        
        self.expect(TokenType.LBRACE)
        self.skip_newlines()
        
        cases = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            case = self.parse_check_case()
            if case:
                cases.append(case)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        
        return ast.CheckStatement(
            value=value,
            cases=cases,
            line=keyword.line,
            column=keyword.column
        )
    
    def parse_check_expression(self) -> ast.CheckStatement:
        """Parse check as an expression (same as statement)."""
        return self.parse_check_statement()
    
    def parse_check_case(self) -> ast.CheckCase:
        """Parse a case in pattern matching: pattern [when guard] => body."""
        pattern = self.parse_pattern()
        
        # Optional guard
        guard = None
        if self.match(TokenType.WHEN):
            guard = self.parse_expression()
        
        self.expect(TokenType.ARROW, "Expected '=>' after pattern")
        
        # Body can be expression or block
        if self.check(TokenType.LBRACE):
            body = self.parse_block()
        else:
            body = self.parse_expression()
        
        self.consume_statement_end()
        
        return ast.CheckCase(
            pattern=pattern,
            guard=guard,
            body=body,
            line=pattern.line,
            column=pattern.column
        )
    
    def parse_pattern(self) -> ast.Node:
        """Parse a pattern for matching."""
        # Wildcard
        if self.check(TokenType.IDENTIFIER) and self.current.value == "_":
            token = self.advance()
            return ast.WildcardPattern(line=token.line, column=token.column)
        
        # Range pattern
        if self.check(TokenType.NUMBER):
            start = self.parse_primary()
            if self.match(TokenType.RANGE) or self.match(TokenType.TO):
                end = self.parse_primary()
                return ast.RangePattern(start=start, end=end)
            return start
        
        # Literal patterns
        if self.check(TokenType.STRING, TokenType.YES, TokenType.NO, TokenType.NONE):
            return self.parse_primary()
        
        # List pattern
        if self.check(TokenType.LBRACKET):
            return self.parse_list_literal()
        
        # Map pattern
        if self.check(TokenType.LBRACE):
            return self.parse_map_literal()
        
        # Type check pattern (is text, is num, etc.)
        # Or binding pattern (identifier)
        if self.check(TokenType.IDENTIFIER):
            token = self.advance()
            return ast.BindingPattern(name=token.value, line=token.line, column=token.column)
        
        raise self.error("Expected pattern")
    
    def parse_try_statement(self) -> ast.TryStatement:
        """Parse: try { } catch e { } [finally { }]."""
        keyword = self.expect(TokenType.TRY)
        try_block = self.parse_block()
        
        self.skip_newlines()
        
        catch_var = None
        catch_block = None
        if self.match(TokenType.CATCH):
            if self.check(TokenType.IDENTIFIER):
                catch_var = self.advance().value
            catch_block = self.parse_block()
        
        self.skip_newlines()
        
        finally_block = None
        if self.match(TokenType.FINALLY):
            finally_block = self.parse_block()
        
        return ast.TryStatement(
            try_block=try_block,
            catch_var=catch_var,
            catch_block=catch_block,
            finally_block=finally_block,
            line=keyword.line,
            column=keyword.column
        )
    
    def parse_give_statement(self) -> ast.GiveStatement:
        """Parse: give [value]."""
        keyword = self.expect(TokenType.GIVE)
        
        value = None
        if not self.is_statement_end():
            value = self.parse_expression()
        
        self.consume_statement_end()
        
        return ast.GiveStatement(
            value=value,
            line=keyword.line,
            column=keyword.column
        )
    
    def parse_fail_statement(self) -> ast.FailStatement:
        """Parse: fail error."""
        keyword = self.expect(TokenType.FAIL)
        error = self.parse_expression()
        self.consume_statement_end()
        
        return ast.FailStatement(
            error=error,
            line=keyword.line,
            column=keyword.column
        )
    
    def parse_import_statement(self) -> ast.ImportStatement:
        """Parse: grab module or grab module.item or grab module.* as alias."""
        keyword = self.expect(TokenType.GRAB)
        
        # Parse module path
        module_parts = [self.expect(TokenType.IDENTIFIER).value]
        
        items = []
        wildcard = False
        
        while self.match(TokenType.DOT):
            if self.match(TokenType.STAR):
                wildcard = True
                break
            part = self.expect(TokenType.IDENTIFIER).value
            module_parts.append(part)
        
        # Check if last part is an item import
        if len(module_parts) > 1 and not wildcard:
            items = [module_parts.pop()]
        
        module = ".".join(module_parts)
        
        # Optional alias
        alias = None
        if self.match(TokenType.AS):
            alias = self.expect(TokenType.IDENTIFIER).value
        
        self.consume_statement_end()
        
        return ast.ImportStatement(
            module=module,
            items=items,
            alias=alias,
            wildcard=wildcard,
            line=keyword.line,
            column=keyword.column
        )
    
    def parse_export_statement(self) -> ast.ExportStatement:
        """Parse: share declaration or share { names }."""
        keyword = self.expect(TokenType.SHARE)
        
        # Export with declaration
        if self.check(TokenType.LET, TokenType.MUT, TokenType.CONST, TokenType.CONDUIT, TokenType.MAKE):
            declaration = self.parse_statement()
            return ast.ExportStatement(
                declaration=declaration,
                line=keyword.line,
                column=keyword.column
            )
        
        # Export names
        if self.match(TokenType.LBRACE):
            names = []
            while not self.check(TokenType.RBRACE):
                names.append(self.expect(TokenType.IDENTIFIER).value)
                if not self.check(TokenType.RBRACE):
                    self.expect(TokenType.COMMA)
            self.expect(TokenType.RBRACE)
            self.consume_statement_end()
            return ast.ExportStatement(
                names=names,
                line=keyword.line,
                column=keyword.column
            )
        
        # Export single name
        name = self.expect(TokenType.IDENTIFIER).value
        self.consume_statement_end()
        return ast.ExportStatement(
            names=[name],
            line=keyword.line,
            column=keyword.column
        )
    
    def parse_expression_statement(self) -> ast.ExpressionStatement:
        """Parse an expression as a statement."""
        expr = self.parse_expression()
        self.consume_statement_end()
        
        return ast.ExpressionStatement(
            expression=expr,
            line=expr.line,
            column=expr.column
        )
    
    # ========================================================================
    # Expressions
    # ========================================================================
    
    def parse_expression(self) -> ast.Node:
        """Parse an expression (entry point)."""
        return self.parse_assignment()
    
    def parse_assignment(self) -> ast.Node:
        """Parse assignment expression."""
        expr = self.parse_pipeline()
        
        if self.check(TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN,
                      TokenType.STAR_ASSIGN, TokenType.SLASH_ASSIGN):
            op_token = self.advance()
            value = self.parse_assignment()  # Right-associative
            
            return ast.Assignment(
                target=expr,
                value=value,
                operator=op_token.value,
                line=op_token.line,
                column=op_token.column
            )
        
        return expr
    
    def parse_pipeline(self) -> ast.Node:
        """Parse pipeline expression: value -> func1 -> func2."""
        expr = self.parse_null_coalesce()
        
        if self.check(TokenType.PIPELINE, TokenType.ASYNC_PIPELINE):
            stages = []
            async_ = False
            
            while self.match(TokenType.PIPELINE, TokenType.ASYNC_PIPELINE):
                if self.tokens[self.pos - 1].type == TokenType.ASYNC_PIPELINE:
                    async_ = True
                stage = self.parse_null_coalesce()
                stages.append(stage)
            
            if stages:
                return ast.Pipeline(
                    value=expr,
                    stages=stages,
                    async_=async_,
                    line=expr.line,
                    column=expr.column
                )
        
        return expr
    
    def parse_null_coalesce(self) -> ast.Node:
        """Parse null coalescing: value ?? default."""
        expr = self.parse_or()
        
        while self.match(TokenType.NULL_COALESCE):
            right = self.parse_or()
            expr = ast.NullCoalesce(
                left=expr,
                right=right,
                line=expr.line,
                column=expr.column
            )
        
        return expr
    
    def parse_or(self) -> ast.Node:
        """Parse logical or."""
        expr = self.parse_and()
        
        while self.match(TokenType.OR):
            right = self.parse_and()
            expr = ast.LogicalOp(
                operator="or",
                left=expr,
                right=right,
                line=expr.line,
                column=expr.column
            )
        
        return expr
    
    def parse_and(self) -> ast.Node:
        """Parse logical and."""
        expr = self.parse_not()
        
        while self.match(TokenType.AND):
            right = self.parse_not()
            expr = ast.LogicalOp(
                operator="and",
                left=expr,
                right=right,
                line=expr.line,
                column=expr.column
            )
        
        return expr
    
    def parse_not(self) -> ast.Node:
        """Parse logical not."""
        if self.match(TokenType.NOT):
            token = self.tokens[self.pos - 1]
            operand = self.parse_not()
            return ast.UnaryOp(
                operator="not",
                operand=operand,
                line=token.line,
                column=token.column
            )
        
        return self.parse_equality()
    
    def parse_equality(self) -> ast.Node:
        """Parse equality: == !=."""
        expr = self.parse_comparison()
        
        while self.check(TokenType.EQ, TokenType.NE):
            op_token = self.advance()
            right = self.parse_comparison()
            expr = ast.BinaryOp(
                operator=op_token.value,
                left=expr,
                right=right,
                line=op_token.line,
                column=op_token.column
            )
        
        return expr
    
    def parse_comparison(self) -> ast.Node:
        """Parse comparison: < > <= >= in."""
        expr = self.parse_range()
        
        # Handle comparison chains: a < b < c
        if self.check(TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE, TokenType.IN):
            operators = []
            operands = [expr]
            
            while self.check(TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE, TokenType.IN):
                op_token = self.advance()
                operators.append(op_token.value)
                operands.append(self.parse_range())
            
            if len(operators) == 1:
                return ast.BinaryOp(
                    operator=operators[0],
                    left=operands[0],
                    right=operands[1],
                    line=expr.line,
                    column=expr.column
                )
            
            return ast.Comparison(
                operators=operators,
                operands=operands,
                line=expr.line,
                column=expr.column
            )
        
        return expr
    
    def parse_range(self) -> ast.Node:
        """Parse range: start..end or start to end."""
        expr = self.parse_addition()
        
        if self.match(TokenType.RANGE, TokenType.TO):
            end = self.parse_addition()
            return ast.Range(
                start=expr,
                end=end,
                line=expr.line,
                column=expr.column
            )
        
        return expr
    
    def parse_addition(self) -> ast.Node:
        """Parse addition and subtraction."""
        expr = self.parse_multiplication()
        
        while self.check(TokenType.PLUS, TokenType.MINUS):
            op_token = self.advance()
            right = self.parse_multiplication()
            expr = ast.BinaryOp(
                operator=op_token.value,
                left=expr,
                right=right,
                line=op_token.line,
                column=op_token.column
            )
        
        return expr
    
    def parse_multiplication(self) -> ast.Node:
        """Parse multiplication, division, modulo."""
        expr = self.parse_power()
        
        while self.check(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op_token = self.advance()
            right = self.parse_power()
            expr = ast.BinaryOp(
                operator=op_token.value,
                left=expr,
                right=right,
                line=op_token.line,
                column=op_token.column
            )
        
        return expr
    
    def parse_power(self) -> ast.Node:
        """Parse exponentiation (right-associative)."""
        expr = self.parse_unary()
        
        if self.match(TokenType.POWER):
            right = self.parse_power()  # Right-associative
            return ast.BinaryOp(
                operator="**",
                left=expr,
                right=right,
                line=expr.line,
                column=expr.column
            )
        
        return expr
    
    def parse_unary(self) -> ast.Node:
        """Parse unary operators: - +."""
        if self.check(TokenType.MINUS, TokenType.PLUS):
            op_token = self.advance()
            operand = self.parse_unary()
            return ast.UnaryOp(
                operator=op_token.value,
                operand=operand,
                line=op_token.line,
                column=op_token.column
            )
        
        return self.parse_await()
    
    def parse_await(self) -> ast.Node:
        """Parse await expression: wait promise."""
        if self.match(TokenType.WAIT):
            token = self.tokens[self.pos - 1]
            expr = self.parse_await()
            return ast.Await(
                expression=expr,
                line=token.line,
                column=token.column
            )
        
        if self.match(TokenType.YIELD):
            token = self.tokens[self.pos - 1]
            expr = None
            if not self.is_statement_end():
                expr = self.parse_expression()
            return ast.Yield(
                expression=expr,
                line=token.line,
                column=token.column
            )
        
        return self.parse_call()
    
    def parse_call(self) -> ast.Node:
        """Parse call, member access, index access."""
        expr = self.parse_primary()
        
        while True:
            if self.match(TokenType.LPAREN):
                # Function call
                args = []
                while not self.check(TokenType.RPAREN):
                    if self.match(TokenType.SPREAD):
                        args.append(ast.SpreadElement(
                            argument=self.parse_expression(),
                            line=self.current.line,
                            column=self.current.column
                        ))
                    else:
                        args.append(self.parse_expression())
                    if not self.check(TokenType.RPAREN):
                        self.expect(TokenType.COMMA)
                self.expect(TokenType.RPAREN)
                expr = ast.Call(
                    callee=expr,
                    arguments=args,
                    line=expr.line,
                    column=expr.column
                )
            elif self.match(TokenType.DOT):
                # Member access
                prop = self.expect(TokenType.IDENTIFIER, "Expected property name")
                expr = ast.MemberAccess(
                    object=expr,
                    property=prop.value,
                    safe=False,
                    line=expr.line,
                    column=expr.column
                )
            elif self.match(TokenType.SAFE_NAV):
                # Safe navigation
                prop = self.expect(TokenType.IDENTIFIER, "Expected property name")
                expr = ast.MemberAccess(
                    object=expr,
                    property=prop.value,
                    safe=True,
                    line=expr.line,
                    column=expr.column
                )
            elif self.match(TokenType.LBRACKET):
                # Index access
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                expr = ast.IndexAccess(
                    object=expr,
                    index=index,
                    safe=False,
                    line=expr.line,
                    column=expr.column
                )
            elif self.match(TokenType.SAFE_INDEX):
                # Safe index access
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                expr = ast.IndexAccess(
                    object=expr,
                    index=index,
                    safe=True,
                    line=expr.line,
                    column=expr.column
                )
            elif self.match(TokenType.DOUBLE_COLON):
                # Static access
                prop = self.expect(TokenType.IDENTIFIER, "Expected static member name")
                expr = ast.StaticAccess(
                    object=expr,
                    property=prop.value,
                    line=expr.line,
                    column=expr.column
                )
            else:
                break
        
        return expr
    
    def parse_primary(self) -> ast.Node:
        """Parse primary expressions."""
        token = self.current
        
        # Literals
        if self.match(TokenType.NUMBER):
            value = token.value
            try:
                if value.startswith('0x') or value.startswith('0X'):
                    num = int(value, 16)
                elif value.startswith('0b') or value.startswith('0B'):
                    num = int(value, 2)
                elif '.' in value or 'e' in value.lower():
                    num = float(value)
                else:
                    num = int(value)
            except ValueError:
                raise self.error(f"Invalid number literal: {value}", token)
            return ast.Literal(value=num, line=token.line, column=token.column)
        
        if self.match(TokenType.STRING):
            # Check if this is part of a template string (followed by INTERP_START)
            if self.check(TokenType.INTERP_START):
                return self.parse_template_string_from_literal(token)
            return ast.Literal(value=token.value, line=token.line, column=token.column)
        
        if self.match(TokenType.YES):
            return ast.Literal(value=True, line=token.line, column=token.column)
        
        if self.match(TokenType.NO):
            return ast.Literal(value=False, line=token.line, column=token.column)
        
        if self.match(TokenType.NONE):
            return ast.Literal(value=None, line=token.line, column=token.column)
        
        # Self reference
        if self.match(TokenType.ME):
            return ast.Me(line=token.line, column=token.column)
        
        if self.match(TokenType.PARENT):
            return ast.Parent(line=token.line, column=token.column)
        
        # Check expression (pattern matching as expression)
        if self.check(TokenType.CHECK):
            return self.parse_check_expression()
        
        # Identifiers
        if self.match(TokenType.IDENTIFIER):
            return ast.Identifier(name=token.value, line=token.line, column=token.column)
        
        # Anonymous function / lambda
        if self.check(TokenType.CONDUIT):
            return self.parse_anonymous_function()
        
        # Grouped expression or lambda parameters
        if self.match(TokenType.LPAREN):
            # Check if this is lambda parameters
            if self.check(TokenType.RPAREN) or self.is_lambda_params():
                return self.parse_lambda_from_lparen()
            
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        # List literal
        if self.check(TokenType.LBRACKET):
            return self.parse_list_literal()
        
        # Map literal
        if self.check(TokenType.LBRACE):
            return self.parse_map_literal()
        
        # Template string parts (from lexer)
        if self.match(TokenType.INTERP_START):
            return self.parse_template_string()
        
        raise self.error(f"Unexpected token: {token.type.name}")
    
    def is_lambda_params(self) -> bool:
        """Check if we're looking at lambda parameters."""
        # Save position
        saved_pos = self.pos
        
        try:
            # Look for pattern: identifier [, identifier]* ) =>
            while not self.check(TokenType.RPAREN, TokenType.EOF):
                if not self.check(TokenType.IDENTIFIER, TokenType.COMMA, TokenType.COLON,
                                  TokenType.ASSIGN, TokenType.SPREAD):
                    return False
                self.advance()
            
            if not self.check(TokenType.RPAREN):
                return False
            self.advance()
            
            return self.check(TokenType.ARROW)
        finally:
            self.pos = saved_pos
    
    def parse_lambda_from_lparen(self) -> ast.Lambda:
        """Parse lambda starting from after (."""
        params = []
        
        while not self.check(TokenType.RPAREN):
            rest = self.match(TokenType.SPREAD)
            name = self.expect(TokenType.IDENTIFIER).value
            
            type_hint = None
            if self.match(TokenType.COLON):
                type_hint = self.expect(TokenType.IDENTIFIER).value
            
            default = None
            if self.match(TokenType.ASSIGN):
                default = self.parse_expression()
            
            params.append(ast.Parameter(
                name=name,
                type_hint=type_hint,
                default=default,
                rest=rest
            ))
            
            if not self.check(TokenType.RPAREN):
                self.expect(TokenType.COMMA)
        
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.ARROW)
        
        # Body is expression or block
        if self.check(TokenType.LBRACE):
            body = self.parse_block()
        else:
            body = self.parse_expression()
        
        return ast.Lambda(
            params=params,
            body=body,
            line=self.current.line,
            column=self.current.column
        )
    
    def parse_anonymous_function(self) -> ast.Lambda:
        """Parse: conduit(params) { body }."""
        self.expect(TokenType.CONDUIT)
        params = self.parse_parameters()
        body = self.parse_block()
        
        return ast.Lambda(
            params=params,
            body=body,
            line=self.current.line,
            column=self.current.column
        )
    
    def parse_list_literal(self) -> ast.ListLiteral:
        """Parse: [elements]."""
        open_bracket = self.expect(TokenType.LBRACKET)
        elements = []
        
        self.skip_newlines()
        while not self.check(TokenType.RBRACKET):
            if self.match(TokenType.SPREAD):
                elements.append(ast.SpreadElement(
                    argument=self.parse_expression(),
                    line=self.current.line,
                    column=self.current.column
                ))
            else:
                elements.append(self.parse_expression())
            
            self.skip_newlines()
            if not self.check(TokenType.RBRACKET):
                self.expect(TokenType.COMMA)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACKET)
        
        return ast.ListLiteral(
            elements=elements,
            line=open_bracket.line,
            column=open_bracket.column
        )
    
    def parse_map_literal(self) -> ast.MapLiteral:
        """Parse: {key: value, ...}."""
        open_brace = self.expect(TokenType.LBRACE)
        entries = []
        
        self.skip_newlines()
        while not self.check(TokenType.RBRACE):
            # Key can be identifier, string, or expression in brackets
            if self.check(TokenType.IDENTIFIER):
                key_token = self.advance()
                key = ast.Literal(value=key_token.value, line=key_token.line, column=key_token.column)
                
                # Shorthand: {name} is same as {name: name}
                if self.check(TokenType.COMMA, TokenType.RBRACE, TokenType.NEWLINE):
                    value = ast.Identifier(name=key_token.value, line=key_token.line, column=key_token.column)
                else:
                    self.expect(TokenType.COLON)
                    value = self.parse_expression()
            elif self.check(TokenType.STRING):
                key_token = self.advance()
                key = ast.Literal(value=key_token.value, line=key_token.line, column=key_token.column)
                self.expect(TokenType.COLON)
                value = self.parse_expression()
            elif self.match(TokenType.LBRACKET):
                # Computed key
                key = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                self.expect(TokenType.COLON)
                value = self.parse_expression()
            elif self.match(TokenType.SPREAD):
                # Spread in map
                key = None
                value = ast.SpreadElement(
                    argument=self.parse_expression(),
                    line=self.current.line,
                    column=self.current.column
                )
            else:
                raise self.error("Expected map key")
            
            entries.append((key, value))
            
            self.skip_newlines()
            if not self.check(TokenType.RBRACE):
                self.expect(TokenType.COMMA)
            self.skip_newlines()
        
        self.expect(TokenType.RBRACE)
        
        return ast.MapLiteral(
            entries=entries,
            line=open_brace.line,
            column=open_brace.column
        )
    
    def parse_template_string(self) -> ast.TemplateString:
        """Parse template string with interpolation starting from INTERP_START."""
        parts = []
        
        # Already consumed INTERP_START, now parse the expression inside
        expr = self.parse_expression()
        parts.append(expr)
        
        # Expect INTERP_END
        if self.check(TokenType.INTERP_END):
            self.advance()
        
        # Continue parsing if more parts follow
        while self.check(TokenType.STRING, TokenType.INTERP_START):
            if self.match(TokenType.STRING):
                token = self.tokens[self.pos - 1]
                parts.append(ast.Literal(value=token.value, line=token.line, column=token.column))
            elif self.match(TokenType.INTERP_START):
                expr = self.parse_expression()
                parts.append(expr)
                if self.check(TokenType.INTERP_END):
                    self.advance()
        
        return ast.TemplateString(
            parts=parts,
            line=self.current.line,
            column=self.current.column
        )
    
    def parse_template_string_from_literal(self, start_token: Token) -> ast.TemplateString:
        """Parse template string starting from a STRING literal."""
        parts = []
        
        # Add the initial string part
        if start_token.value:
            parts.append(ast.Literal(value=start_token.value, line=start_token.line, column=start_token.column))
        
        # Continue parsing template string parts
        while self.check(TokenType.INTERP_START, TokenType.STRING):
            if self.match(TokenType.INTERP_START):
                # Parse expression inside ${}
                expr = self.parse_expression()
                parts.append(expr)
                # Expect INTERP_END
                if self.check(TokenType.INTERP_END):
                    self.advance()
            elif self.match(TokenType.STRING):
                token = self.tokens[self.pos - 1]
                if token.value:  # Only add non-empty strings
                    parts.append(ast.Literal(value=token.value, line=token.line, column=token.column))
        
        return ast.TemplateString(
            parts=parts,
            line=start_token.line,
            column=start_token.column
        )


def parse(source: str, filename: str = "<stdin>") -> ast.Program:
    """Convenience function to parse source code."""
    tokens = tokenize(source, filename)
    parser = Parser(tokens, filename)
    return parser.parse()
