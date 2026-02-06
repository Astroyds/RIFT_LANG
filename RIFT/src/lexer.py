"""
RIFT Language Lexer

Tokenization engine that breaks source code into tokens for the parser.
Handles all RIFT keywords, operators, and literals.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Iterator
import re

from .errors import LexerError


class TokenType(Enum):
    """All token types in the RIFT language."""
    # Literals
    NUMBER = auto()
    STRING = auto()
    TEMPLATE_STRING = auto()
    IDENTIFIER = auto()
    
    # Keywords
    CONDUIT = auto()      # conduit (function)
    LET = auto()          # let (immutable variable)
    MUT = auto()          # mut (mutable variable)
    CONST = auto()        # const (compile-time constant)
    GIVE = auto()         # give (return)
    STOP = auto()         # stop (break)
    NEXT = auto()         # next (continue)
    IF = auto()           # if
    ELSE = auto()         # else
    CHECK = auto()        # check (pattern matching)
    REPEAT = auto()       # repeat (for loop)
    WHILE = auto()        # while
    TRY = auto()          # try
    CATCH = auto()        # catch
    FINALLY = auto()      # finally
    FAIL = auto()         # fail (throw)
    MAKE = auto()         # make (class)
    EXTEND = auto()       # extend (inheritance)
    BUILD = auto()        # build (constructor)
    ME = auto()           # me (self/this)
    PARENT = auto()       # parent (super)
    GRAB = auto()         # grab (import)
    SHARE = auto()        # share (export)
    WAIT = auto()         # wait (await)
    ASYNC = auto()        # async
    YES = auto()          # yes (true)
    NO = auto()           # no (false)
    NONE = auto()         # none (null)
    AND = auto()          # and
    OR = auto()           # or
    NOT = auto()          # not
    IN = auto()           # in
    AS = auto()           # as
    YIELD = auto()        # yield
    WHEN = auto()         # when (guard clause)
    TO = auto()           # to (range)
    STATIC = auto()       # static
    GET = auto()          # get (getter)
    SET = auto()          # set (setter)
    
    # Arithmetic Operators
    PLUS = auto()         # +
    MINUS = auto()        # -
    STAR = auto()         # *
    SLASH = auto()        # /
    PERCENT = auto()      # %
    POWER = auto()        # **
    
    # Comparison Operators
    EQ = auto()           # ==
    NE = auto()           # !=
    LT = auto()           # <
    GT = auto()           # >
    LE = auto()           # <=
    GE = auto()           # >=
    
    # Special Operators
    NULL_COALESCE = auto()    # ??
    SAFE_NAV = auto()         # ?.
    SAFE_INDEX = auto()       # ?[
    PIPELINE = auto()         # ->
    REV_PIPELINE = auto()     # <-
    ASYNC_PIPELINE = auto()   # ~>
    ARROW = auto()            # =>
    DOUBLE_COLON = auto()     # ::
    RANGE = auto()            # ..
    SPREAD = auto()           # ...
    
    # Assignment
    ASSIGN = auto()       # =
    PLUS_ASSIGN = auto()  # +=
    MINUS_ASSIGN = auto() # -=
    STAR_ASSIGN = auto()  # *=
    SLASH_ASSIGN = auto() # /=
    
    # Delimiters
    LPAREN = auto()       # (
    RPAREN = auto()       # )
    LBRACE = auto()       # @ (block open)
    RBRACE = auto()       # # (block close)
    LBRACKET = auto()     # ~ (array open)
    RBRACKET = auto()     # ! (array close)
    COMMA = auto()        # ,
    DOT = auto()          # .
    COLON = auto()        # :
    SEMICOLON = auto()    # ;
    
    # Special
    NEWLINE = auto()
    EOF = auto()
    
    # Interpolation markers
    INTERP_START = auto()  # $@
    INTERP_END = auto()    # # in template context


@dataclass
class Token:
    """A token from the lexer."""
    type: TokenType
    value: str
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


# Keyword mapping
KEYWORDS = {
    'conduit': TokenType.CONDUIT,
    'let': TokenType.LET,
    'mut': TokenType.MUT,
    'const': TokenType.CONST,
    'give': TokenType.GIVE,
    'stop': TokenType.STOP,
    'next': TokenType.NEXT,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'check': TokenType.CHECK,
    'repeat': TokenType.REPEAT,
    'while': TokenType.WHILE,
    'try': TokenType.TRY,
    'catch': TokenType.CATCH,
    'finally': TokenType.FINALLY,
    'fail': TokenType.FAIL,
    'make': TokenType.MAKE,
    'extend': TokenType.EXTEND,
    'build': TokenType.BUILD,
    'me': TokenType.ME,
    'parent': TokenType.PARENT,
    'grab': TokenType.GRAB,
    'share': TokenType.SHARE,
    'wait': TokenType.WAIT,
    'async': TokenType.ASYNC,
    'yes': TokenType.YES,
    'no': TokenType.NO,
    'none': TokenType.NONE,
    'and': TokenType.AND,
    'or': TokenType.OR,
    'not': TokenType.NOT,
    'in': TokenType.IN,
    'as': TokenType.AS,
    'yield': TokenType.YIELD,
    'when': TokenType.WHEN,
    'to': TokenType.TO,
    'static': TokenType.STATIC,
    # Note: 'get' and 'set' are contextual keywords, only valid inside class definitions
    # They are handled specially in the parser for class member parsing
}


class Lexer:
    """
    Tokenizer for the RIFT language.
    
    Handles:
    - Keywords and identifiers
    - String literals with interpolation
    - Number literals (decimal, hex, binary, scientific)
    - All operators including multi-character ones
    - Comments (single-line # and multi-line /* */)
    """
    
    def __init__(self, source: str, filename: str = "<stdin>"):
        self.source = source
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.in_template = False
        self.template_depth = 0
    
    def error(self, message: str) -> LexerError:
        return LexerError(message, self.line, self.column, self.filename)
    
    @property
    def current(self) -> str:
        """Current character or empty string if at end."""
        if self.pos >= len(self.source):
            return ''
        return self.source[self.pos]
    
    def peek(self, offset: int = 1) -> str:
        """Look ahead by offset characters."""
        pos = self.pos + offset
        if pos >= len(self.source):
            return ''
        return self.source[pos]
    
    def peek_str(self, length: int) -> str:
        """Look ahead by multiple characters."""
        return self.source[self.pos:self.pos + length]
    
    def advance(self) -> str:
        """Consume and return current character."""
        char = self.current
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char
    
    def skip_whitespace(self):
        """Skip spaces and tabs (not newlines)."""
        while self.current in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        """Skip single-line comment."""
        while self.current and self.current != '\n':
            self.advance()
    
    def skip_multiline_comment(self):
        """Skip multi-line comment /* ... */."""
        self.advance()  # consume /
        self.advance()  # consume *
        while self.current:
            if self.current == '*' and self.peek() == '/':
                self.advance()  # consume *
                self.advance()  # consume /
                return
            self.advance()
        raise self.error("Unterminated multi-line comment")
    
    def make_token(self, type: TokenType, value: str) -> Token:
        """Create a token at current position."""
        # Calculate column at start of token
        col = self.column - len(value)
        if col < 1:
            col = 1
        return Token(type, value, self.line, col)
    
    def read_string(self, quote: str) -> Token:
        """Read a string literal."""
        start_line = self.line
        start_col = self.column
        self.advance()  # consume opening quote
        value = ""
        
        while self.current and self.current != quote:
            if self.current == '\\':
                self.advance()  # consume backslash
                escape = self.current
                if escape == 'n':
                    value += '\n'
                elif escape == 't':
                    value += '\t'
                elif escape == 'r':
                    value += '\r'
                elif escape == '\\':
                    value += '\\'
                elif escape == quote:
                    value += quote
                elif escape == '0':
                    value += '\0'
                else:
                    value += escape
                self.advance()
            elif self.current == '\n':
                value += self.current
                self.advance()
            else:
                value += self.current
                self.advance()
        
        if not self.current:
            raise LexerError("Unterminated string", start_line, start_col, self.filename)
        
        self.advance()  # consume closing quote
        return Token(TokenType.STRING, value, start_line, start_col)
    
    def read_template_string(self) -> List[Token]:
        """Read a template string with interpolation."""
        tokens = []
        start_line = self.line
        start_col = self.column
        self.advance()  # consume opening backtick
        value = ""
        
        while self.current and self.current != '`':
            if self.current == '$' and self.peek() == '@':
                # Emit any accumulated string content
                if value:
                    tokens.append(Token(TokenType.STRING, value, start_line, start_col))
                    value = ""
                
                # Emit interpolation start
                self.advance()  # consume $
                self.advance()  # consume @
                tokens.append(Token(TokenType.INTERP_START, '$@', self.line, self.column - 2))
                
                # Tokenize the interpolated expression
                brace_depth = 1
                interp_start = self.pos
                while self.current and brace_depth > 0:
                    if self.current == '@':
                        brace_depth += 1
                    elif self.current == '#':
                        brace_depth -= 1
                        if brace_depth == 0:
                            break
                    self.advance()
                
                # Create sub-lexer for the interpolated content
                interp_source = self.source[interp_start:self.pos]
                if interp_source.strip():
                    sub_lexer = Lexer(interp_source, self.filename)
                    sub_tokens = sub_lexer.tokenize()
                    # Remove EOF token from sub-tokens
                    tokens.extend([t for t in sub_tokens if t.type != TokenType.EOF])
                
                # Emit interpolation end
                if self.current == '#':
                    tokens.append(Token(TokenType.INTERP_END, '#', self.line, self.column))
                    self.advance()  # consume #
                
                start_line = self.line
                start_col = self.column
            elif self.current == '\\':
                self.advance()
                escape = self.current
                if escape == 'n':
                    value += '\n'
                elif escape == 't':
                    value += '\t'
                elif escape == 'r':
                    value += '\r'
                elif escape == '\\':
                    value += '\\'
                elif escape == '`':
                    value += '`'
                elif escape == '$':
                    value += '$'
                else:
                    value += escape
                self.advance()
            else:
                value += self.current
                self.advance()
        
        if not self.current:
            raise LexerError("Unterminated template string", start_line, start_col, self.filename)
        
        if value:
            tokens.append(Token(TokenType.STRING, value, start_line, start_col))
        
        self.advance()  # consume closing backtick
        return tokens
    
    def read_number(self) -> Token:
        """Read a number literal."""
        start_col = self.column
        value = ""
        
        # Check for hex or binary
        if self.current == '0':
            if self.peek() in 'xX':
                value += self.advance()  # 0
                value += self.advance()  # x
                while self.current and (self.current.isalnum() or self.current == '_'):
                    if self.current != '_':
                        value += self.current
                    self.advance()
                return Token(TokenType.NUMBER, value, self.line, start_col)
            elif self.peek() in 'bB':
                value += self.advance()  # 0
                value += self.advance()  # b
                while self.current and self.current in '01_':
                    if self.current != '_':
                        value += self.current
                    self.advance()
                return Token(TokenType.NUMBER, value, self.line, start_col)
        
        # Read integer part
        while self.current and (self.current.isdigit() or self.current == '_'):
            if self.current != '_':
                value += self.current
            self.advance()
        
        # Check for decimal point
        if self.current == '.' and self.peek() != '.':  # Not range operator
            value += self.advance()
            while self.current and (self.current.isdigit() or self.current == '_'):
                if self.current != '_':
                    value += self.current
                self.advance()
        
        # Check for scientific notation
        if self.current in 'eE':
            value += self.advance()
            if self.current in '+-':
                value += self.advance()
            while self.current and self.current.isdigit():
                value += self.current
                self.advance()
        
        return Token(TokenType.NUMBER, value, self.line, start_col)
    
    def read_identifier(self) -> Token:
        """Read an identifier or keyword."""
        start_col = self.column
        value = ""
        
        while self.current and (self.current.isalnum() or self.current == '_'):
            value += self.current
            self.advance()
        
        # Check if it's a keyword
        token_type = KEYWORDS.get(value, TokenType.IDENTIFIER)
        return Token(token_type, value, self.line, start_col)
    
    def read_operator(self) -> Token:
        """Read an operator."""
        start_col = self.column
        
        # Three-character operators
        three = self.peek_str(3)
        if three == '...':
            self.advance()
            self.advance()
            self.advance()
            return Token(TokenType.SPREAD, '...', self.line, start_col)
        
        # Two-character operators
        two = self.peek_str(2)
        two_char_ops = {
            '==': TokenType.EQ,
            '!=': TokenType.NE,
            '<=': TokenType.LE,
            '>=': TokenType.GE,
            '**': TokenType.POWER,
            '??': TokenType.NULL_COALESCE,
            '?.': TokenType.SAFE_NAV,
            '?~': TokenType.SAFE_INDEX,
            '->': TokenType.PIPELINE,
            '=>': TokenType.ARROW,
            '::': TokenType.DOUBLE_COLON,
            '..': TokenType.RANGE,
            '+=': TokenType.PLUS_ASSIGN,
            '-=': TokenType.MINUS_ASSIGN,
            '*=': TokenType.STAR_ASSIGN,
            '/=': TokenType.SLASH_ASSIGN,
        }
        
        if two in two_char_ops:
            self.advance()
            self.advance()
            return Token(two_char_ops[two], two, self.line, start_col)
        
        # Single-character operators
        one_char_ops = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.STAR,
            '/': TokenType.SLASH,
            '%': TokenType.PERCENT,
            '<': TokenType.LT,
            '>': TokenType.GT,
            '=': TokenType.ASSIGN,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '@': TokenType.LBRACE,    # Block open
            '#': TokenType.RBRACE,    # Block close
            '~': TokenType.LBRACKET,  # Array open
            '!': TokenType.RBRACKET,  # Array close
            ',': TokenType.COMMA,
            '.': TokenType.DOT,
            ':': TokenType.COLON,
            ';': TokenType.SEMICOLON,
        }
        
        char = self.current
        if char in one_char_ops:
            self.advance()
            return Token(one_char_ops[char], char, self.line, start_col)
        
        raise self.error(f"Unexpected character: {char!r}")
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code."""
        self.tokens = []
        
        while self.current:
            # Skip whitespace (not newlines)
            if self.current in ' \t\r':
                self.skip_whitespace()
                continue
            
            # Handle newlines
            if self.current == '\n':
                self.tokens.append(self.make_token(TokenType.NEWLINE, '\n'))
                self.advance()
                continue
            
            # Skip comments (only multi-line /* */ style now, since # is block close)
            if self.current == '/' and self.peek() == '*':
                self.skip_multiline_comment()
                continue
            
            # String literals
            if self.current in '"\'':
                self.tokens.append(self.read_string(self.current))
                continue
            
            # Template strings
            if self.current == '`':
                self.tokens.extend(self.read_template_string())
                continue
            
            # Numbers
            if self.current.isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # Identifiers and keywords
            if self.current.isalpha() or self.current == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # Operators and delimiters
            self.tokens.append(self.read_operator())
        
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens


def tokenize(source: str, filename: str = "<stdin>") -> List[Token]:
    """Convenience function to tokenize source code."""
    lexer = Lexer(source, filename)
    return lexer.tokenize()
