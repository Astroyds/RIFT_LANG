"""
RIFT Standard Library - WebSocket Module

WebSocket server and client functionality.
"""

import socket
import hashlib
import base64
import struct
import threading
from typing import Dict, Any, Optional, Callable


def create_websocket_module(interpreter) -> Dict[str, Any]:
    """Create the WebSocket module for RIFT."""
    
    class WebSocketServer:
        """Simple WebSocket server."""
        
        def __init__(self, host: str = '0.0.0.0', port: int = 8765):
            self.host = host
            self.port = port
            self._clients: Dict[str, socket.socket] = {}
            self._handlers: Dict[str, Callable] = {}
            self._running = False
            self._server_socket = None
        
        def on_connect(self, handler):
            """Register connection handler."""
            self._handlers['connect'] = handler
        
        def on_message(self, handler):
            """Register message handler."""
            self._handlers['message'] = handler
        
        def on_disconnect(self, handler):
            """Register disconnect handler."""
            self._handlers['disconnect'] = handler
        
        def broadcast(self, message: str):
            """Broadcast message to all clients."""
            for client_id, client_socket in list(self._clients.items()):
                try:
                    self._send_message(client_socket, message)
                except:
                    del self._clients[client_id]
        
        def send(self, client_id: str, message: str):
            """Send message to specific client."""
            if client_id in self._clients:
                self._send_message(self._clients[client_id], message)
        
        def _send_message(self, sock: socket.socket, message: str):
            """Send WebSocket frame."""
            data = message.encode('utf-8')
            header = bytearray([0x81])  # Text frame
            
            length = len(data)
            if length <= 125:
                header.append(length)
            elif length <= 65535:
                header.append(126)
                header.extend(struct.pack('>H', length))
            else:
                header.append(127)
                header.extend(struct.pack('>Q', length))
            
            sock.sendall(header + data)
        
        def _receive_message(self, sock: socket.socket) -> Optional[str]:
            """Receive WebSocket frame."""
            try:
                header = sock.recv(2)
                if len(header) != 2:
                    return None
                
                opcode = header[0] & 0x0F
                masked = header[1] & 0x80
                length = header[1] & 0x7F
                
                if length == 126:
                    length = struct.unpack('>H', sock.recv(2))[0]
                elif length == 127:
                    length = struct.unpack('>Q', sock.recv(8))[0]
                
                mask = sock.recv(4) if masked else None
                data = bytearray(sock.recv(length))
                
                if masked and mask:
                    for i in range(len(data)):
                        data[i] ^= mask[i % 4]
                
                if opcode == 0x01:  # Text frame
                    return data.decode('utf-8')
                elif opcode == 0x08:  # Close frame
                    return None
                
                return None
            except:
                return None
        
        def _handle_client(self, client_socket: socket.socket, client_addr):
            """Handle client connection."""
            client_id = f"{client_addr[0]}:{client_addr[1]}"
            
            try:
                # WebSocket handshake
                request = client_socket.recv(1024).decode('utf-8')
                
                # Extract WebSocket key
                key_match = None
                for line in request.split('\r\n'):
                    if 'Sec-WebSocket-Key' in line:
                        key_match = line.split(': ')[1]
                        break
                
                if not key_match:
                    client_socket.close()
                    return
                
                # Generate accept key
                magic = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
                accept = base64.b64encode(
                    hashlib.sha1((key_match + magic).encode()).digest()
                ).decode()
                
                # Send handshake response
                response = (
                    'HTTP/1.1 101 Switching Protocols\r\n'
                    'Upgrade: websocket\r\n'
                    'Connection: Upgrade\r\n'
                    f'Sec-WebSocket-Accept: {accept}\r\n'
                    '\r\n'
                )
                client_socket.sendall(response.encode())
                
                # Store client
                self._clients[client_id] = client_socket
                
                # Call connect handler
                if 'connect' in self._handlers:
                    interpreter._call(self._handlers['connect'], [client_id], None)
                
                # Message loop
                while self._running:
                    message = self._receive_message(client_socket)
                    if message is None:
                        break
                    
                    if 'message' in self._handlers:
                        interpreter._call(self._handlers['message'], 
                                        [client_id, message], None)
                
            except:
                pass
            finally:
                # Call disconnect handler
                if 'disconnect' in self._handlers:
                    interpreter._call(self._handlers['disconnect'], [client_id], None)
                
                if client_id in self._clients:
                    del self._clients[client_id]
                
                client_socket.close()
        
        def start(self):
            """Start WebSocket server."""
            self._running = True
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind((self.host, self.port))
            self._server_socket.listen(5)
            
            print(f"WebSocket server running on ws://{self.host}:{self.port}")
            
            while self._running:
                try:
                    client_socket, client_addr = self._server_socket.accept()
                    thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_addr)
                    )
                    thread.daemon = True
                    thread.start()
                except:
                    break
        
        def stop(self):
            """Stop WebSocket server."""
            self._running = False
            if self._server_socket:
                self._server_socket.close()
    
    return {
        'WebSocketServer': WebSocketServer,
        'createServer': lambda host='0.0.0.0', port=8765: WebSocketServer(host, port)
    }
