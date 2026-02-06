#!/usr/bin/env python3
"""
RIFT Server Runtime

Server runtime for RIFT applications, similar to Node.js.

Usage:
    riftserver app.rift              # Start server
    riftserver app.rift --port 3000  # Start on specific port
    riftserver app.rift --watch      # Hot reload on changes
    riftserver app.rift --workers 4  # Multi-process mode
"""

import sys
import os
import argparse
import signal
import time
import multiprocessing
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.lexer import tokenize
from src.parser import parse
from src.interpreter import Interpreter
from src.errors import RiftError
from src import __version__


class RiftServer:
    """
    RIFT Server Runtime.
    
    Provides:
    - Persistent server process
    - HTTP/HTTPS server integration
    - Hot reload for development
    - Multi-process clustering
    - Graceful shutdown handling
    """
    
    def __init__(self):
        self.running = False
        self.interpreter = None
        self.script_path = None
        self.last_modified = 0
        self.workers = []
    
    def load_script(self, path: str) -> bool:
        """Load and execute a RIFT script."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            self.script_path = path
            self.last_modified = os.path.getmtime(path)
            
            # Parse and execute
            ast = parse(source, path)
            self.interpreter = Interpreter()
            self.interpreter.execute(ast)
            
            return True
        
        except FileNotFoundError:
            print(f"Error: File not found: {path}", file=sys.stderr)
            return False
        except RiftError as e:
            print(f"Error: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Internal error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return False
    
    def start(self, path: str, port: int = 8080, host: str = '0.0.0.0',
              watch: bool = False, workers: int = 1, daemon: bool = False,
              pid_file: str = None):
        """Start the server runtime."""
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        
        # Write PID file if requested
        if pid_file:
            with open(pid_file, 'w') as f:
                f.write(str(os.getpid()))
        
        # Multi-worker mode
        if workers > 1:
            self._start_workers(path, port, host, workers, watch)
            return
        
        # Single process mode
        self.running = True
        
        if not self.load_script(path):
            return
        
        print(f"RIFT Server {__version__}")
        print(f"Script: {path}")
        
        if watch:
            print("Hot reload enabled - watching for changes")
            self._watch_loop(path)
        else:
            # Keep process alive
            self._run_loop()
    
    def _start_workers(self, path: str, port: int, host: str,
                       num_workers: int, watch: bool):
        """Start multiple worker processes."""
        print(f"RIFT Server {__version__}")
        print(f"Starting {num_workers} workers...")
        
        self.running = True
        
        for i in range(num_workers):
            worker_port = port + i  # Each worker on different port
            p = multiprocessing.Process(
                target=self._worker_process,
                args=(path, worker_port, host, watch)
            )
            p.start()
            self.workers.append(p)
            print(f"  Worker {i+1} started on port {worker_port}")
        
        # Monitor workers
        try:
            while self.running:
                for i, p in enumerate(self.workers):
                    if not p.is_alive():
                        print(f"Worker {i+1} died, restarting...")
                        worker_port = port + i
                        new_p = multiprocessing.Process(
                            target=self._worker_process,
                            args=(path, worker_port, host, watch)
                        )
                        new_p.start()
                        self.workers[i] = new_p
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        # Shutdown workers
        for p in self.workers:
            p.terminate()
            p.join(timeout=5)
    
    def _worker_process(self, path: str, port: int, host: str, watch: bool):
        """Worker process main function."""
        server = RiftServer()
        server.start(path, port, host, watch, workers=1)
    
    def _run_loop(self):
        """Main run loop."""
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
    
    def _watch_loop(self, path: str):
        """Watch loop with hot reload."""
        try:
            while self.running:
                # Check for file changes
                try:
                    current_mtime = os.path.getmtime(path)
                    if current_mtime > self.last_modified:
                        print(f"\nFile changed, reloading {path}...")
                        if self.load_script(path):
                            print("Reload successful")
                        else:
                            print("Reload failed, using previous version")
                except FileNotFoundError:
                    pass
                
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
    
    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals."""
        print("\nShutting down...")
        self.running = False
        
        # Stop HTTP server if running
        if self.interpreter and 'http' in self.interpreter.modules:
            try:
                http_module = self.interpreter.modules['http']
                if hasattr(http_module, 'stop'):
                    http_module['stop']()
            except Exception:
                pass
        
        # Terminate workers
        for p in self.workers:
            p.terminate()
        
        sys.exit(0)
    
    def stop(self):
        """Stop the server."""
        self.running = False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="RIFT Server Runtime",
        prog="riftserver"
    )
    parser.add_argument(
        'file',
        help='RIFT script file to run'
    )
    parser.add_argument(
        '-p', '--port',
        type=int,
        default=8080,
        help='Port to listen on (default: 8080)'
    )
    parser.add_argument(
        '-H', '--host',
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    parser.add_argument(
        '-w', '--watch',
        action='store_true',
        help='Enable hot reload on file changes'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Number of worker processes (default: 1)'
    )
    parser.add_argument(
        '-d', '--daemon',
        action='store_true',
        help='Run as daemon'
    )
    parser.add_argument(
        '--pid-file',
        help='Write process ID to file'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'RIFT Server {__version__}'
    )
    
    args = parser.parse_args()
    
    # Resolve file path
    script_path = os.path.abspath(args.file)
    
    if not os.path.exists(script_path):
        print(f"Error: File not found: {script_path}", file=sys.stderr)
        sys.exit(1)
    
    # Change to script directory
    os.chdir(os.path.dirname(script_path))
    
    # Start server
    server = RiftServer()
    server.start(
        script_path,
        port=args.port,
        host=args.host,
        watch=args.watch,
        workers=args.workers,
        daemon=args.daemon,
        pid_file=args.pid_file
    )


if __name__ == '__main__':
    main()
