#!/usr/bin/env python3
"""
RIFT Language CLI

Command-line interface and REPL for the RIFT programming language.

Usage:
    rift script.rift         # Run a RIFT script
    rift repl                # Start interactive REPL
    rift --version           # Show version
    rift --help              # Show help
"""

import sys
import os
import argparse
import traceback

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.lexer import tokenize, LexerError
from src.parser import parse, ParseError
from src.interpreter import Interpreter, interpret
from src.errors import RiftError
from src import __version__


def run_file(filename: str, debug: bool = False) -> int:
    """Run a RIFT script file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filename}", file=sys.stderr)
        return 1
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1
    
    try:
        if debug:
            # Show tokens
            tokens = tokenize(source, filename)
            print("=== Tokens ===")
            for token in tokens:
                print(f"  {token}")
            print()
            
            # Show AST
            ast = parse(source, filename)
            print("=== AST ===")
            print_ast(ast, 0)
            print()
            
            print("=== Output ===")
        
        # Execute
        result = interpret(source, filename)
        
        if debug and result is not None:
            print(f"\n=== Result ===")
            print(f"  {result!r}")
        
        return 0
    
    except RiftError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Internal error: {e}", file=sys.stderr)
        if debug:
            traceback.print_exc()
        return 1


def print_ast(node, indent: int):
    """Pretty print AST for debugging."""
    prefix = "  " * indent
    if node is None:
        print(f"{prefix}None")
        return
    
    name = node.__class__.__name__
    
    if hasattr(node, '__dataclass_fields__'):
        print(f"{prefix}{name}(")
        for field in node.__dataclass_fields__:
            value = getattr(node, field)
            if isinstance(value, list):
                print(f"{prefix}  {field}=[")
                for item in value:
                    print_ast(item, indent + 2)
                print(f"{prefix}  ]")
            elif hasattr(value, '__dataclass_fields__'):
                print(f"{prefix}  {field}=")
                print_ast(value, indent + 2)
            else:
                print(f"{prefix}  {field}={value!r}")
        print(f"{prefix})")
    else:
        print(f"{prefix}{name}: {node!r}")


def run_repl():
    """Run the interactive REPL."""
    print(f"RIFT {__version__} Interactive Shell")
    print("Type 'exit' or 'quit' to exit, 'help' for help.")
    print()
    
    interpreter = Interpreter()
    buffer = []
    
    while True:
        try:
            prompt = ">>> " if not buffer else "... "
            line = input(prompt)
        except EOFError:
            print("\nGoodbye!")
            break
        except KeyboardInterrupt:
            print("\n")
            buffer = []
            continue
        
        # Handle commands
        if not buffer:
            if line.strip() in ('exit', 'quit'):
                print("Goodbye!")
                break
            if line.strip() == 'help':
                print_repl_help()
                continue
            if line.strip() == 'clear':
                os.system('clear' if os.name != 'nt' else 'cls')
                continue
        
        # Handle multi-line input
        buffer.append(line)
        source = '\n'.join(buffer)
        
        # Check if we need more input
        if needs_more_input(source):
            continue
        
        # Execute
        buffer = []
        
        if not source.strip():
            continue
        
        try:
            ast = parse(source, "<repl>")
            result = interpreter.execute(ast)
            
            if result is not None:
                print(format_value(result))
        
        except RiftError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Internal error: {e}")


def needs_more_input(source: str) -> bool:
    """Check if source code needs more input."""
    # Count braces, brackets, parentheses
    # Note: @ is block open, # is block close, ~ is array open, ! is array close
    opens = source.count('@') + source.count('~') + source.count('(')
    closes = source.count('#') + source.count('!') + source.count(')')
    
    if opens > closes:
        return True
    
    # Check for trailing operators
    stripped = source.strip()
    if stripped.endswith(('and', 'or', '->', '~>', '+', '-', '*', '/', '=', ',')):
        return True
    
    return False


def format_value(value) -> str:
    """Format a value for REPL output."""
    if value is None:
        return 'none'
    if isinstance(value, bool):
        return 'yes' if value else 'no'
    if isinstance(value, str):
        return repr(value)
    if isinstance(value, list):
        items = ', '.join(format_value(x) for x in value)
        return f'[{items}]'
    if isinstance(value, dict):
        items = ', '.join(f'{k}: {format_value(v)}' for k, v in value.items())
        return f'{{{items}}}'
    return repr(value)


def print_repl_help():
    """Print REPL help."""
    print("""
RIFT REPL Commands:
  help     Show this help message
  clear    Clear the screen
  exit     Exit the REPL
  quit     Exit the REPL

Language Basics:
  let x = 10           Immutable variable
  mut y = 20           Mutable variable
  print("Hello")       Print to console
  
  conduit add(a, b) {  Function definition
      give a + b
  }
  
  if x > 5 {           Conditional
      print("big")
  }
  
  repeat i in 1..10 {  For loop
      print(i)
  }
  
  grab http            Import module
  grab crypto.hash     Import specific function

For more information, see the RIFT documentation.
""")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="RIFT - Rapid Integrated Framework Technology",
        prog="rift"
    )
    parser.add_argument(
        'file',
        nargs='?',
        help='RIFT script file to run'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'RIFT {__version__}'
    )
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Enable debug output (show tokens and AST)'
    )
    parser.add_argument(
        '-e', '--eval',
        metavar='CODE',
        help='Evaluate RIFT code from command line'
    )
    parser.add_argument(
        'repl',
        nargs='?',
        help='Start interactive REPL'
    )
    
    args = parser.parse_args()
    
    # Evaluate code from command line
    if args.eval:
        try:
            result = interpret(args.eval, "<eval>")
            if result is not None:
                print(format_value(result))
            sys.exit(0)
        except RiftError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Run file
    if args.file:
        if args.file == 'repl':
            run_repl()
        else:
            sys.exit(run_file(args.file, args.debug))
    else:
        # No arguments, start REPL
        run_repl()


if __name__ == '__main__':
    main()
