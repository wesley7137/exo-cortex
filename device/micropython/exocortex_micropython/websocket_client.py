import usocket as socket
import ubinascii as binascii
import urandom as random
import ussl as ssl
import json
from micropython import const

# WebSocket opcodes
OPCODE_CONT = const(0x0)
OPCODE_TEXT = const(0x1)
OPCODE_BINARY = const(0x2)
OPCODE_CLOSE = const(0x8)
OPCODE_PING = const(0x9)
OPCODE_PONG = const(0xa)

class WebSocketClient:
    def __init__(self, url):
        self.url = url
        self.socket = None
        self.connected = False
        self._handshake_done = False
        
        # Parse URL
        proto, dummy, host, path = url.split('/', 3)
        if ':' in host:
            host, port = host.split(':')
            port = int(port)
        else:
            port = 80 if proto == 'ws' else 443
            
        self.host = host
        self.port = port
        self.path = f'/{path}'
        self.ssl = proto == 'wss'
        
    def connect(self):
        try:
            self.socket = socket.socket()
            addr = socket.getaddrinfo(self.host, self.port)[0][-1]
            self.socket.connect(addr)
            
            if self.ssl:
                self.socket = ssl.wrap_socket(self.socket)
                
            # Generate random key for handshake
            key = binascii.b2a_base64(bytes(random.getrandbits(8) for _ in range(16)))[:-1]
            
            # Send handshake request
            handshake = (
                f'GET {self.path} HTTP/1.1\r\n'
                f'Host: {self.host}:{self.port}\r\n'
                'Connection: Upgrade\r\n'
                'Upgrade: websocket\r\n'
                'Sec-WebSocket-Version: 13\r\n'
                f'Sec-WebSocket-Key: {key.decode()}\r\n'
                '\r\n'
            )
            self.socket.write(handshake.encode())
            
            # Verify handshake response
            response = self.socket.readline()
            if b'101 Switching Protocols' not in response:
                raise Exception('Invalid handshake response')
                
            # Skip headers
            while self.socket.readline().strip():
                pass
                
            self.connected = True
            self._handshake_done = True
            print('WebSocket connected')
            return True
            
        except Exception as e:
            print(f'WebSocket connection failed: {e}')
            self.close()
            return False
            
    def close(self):
        if self.connected:
            # Send close frame
            self._send_frame(OPCODE_CLOSE, b'')
            self.socket.close()
            self.connected = False
            self._handshake_done = False
            
    def send_text(self, data):
        if not self.connected:
            return False
        try:
            self._send_frame(OPCODE_TEXT, data.encode())
            return True
        except:
            self.close()
            return False
            
    def send_binary(self, data):
        if not self.connected:
            return False
        try:
            self._send_frame(OPCODE_BINARY, data)
            return True
        except:
            self.close()
            return False
            
    def receive(self):
        if not self.connected:
            return None
            
        try:
            opcode, data = self._read_frame()
            
            if opcode == OPCODE_TEXT:
                return data.decode()
            elif opcode == OPCODE_BINARY:
                return data
            elif opcode == OPCODE_PING:
                self._send_frame(OPCODE_PONG, data)
                return self.receive()  # Get next message
            elif opcode == OPCODE_PONG:
                return self.receive()  # Get next message
            elif opcode == OPCODE_CLOSE:
                self.close()
                return None
                
        except:
            self.close()
            return None
            
    def _send_frame(self, opcode, data):
        length = len(data)
        frame = bytearray()
        frame.append(0x80 | opcode)  # FIN + opcode
        
        if length < 126:
            frame.append(length)
        elif length < 65536:
            frame.append(126)
            frame.extend(length.to_bytes(2, 'big'))
        else:
            frame.append(127)
            frame.extend(length.to_bytes(8, 'big'))
            
        frame.extend(data)
        self.socket.write(frame)
        
    def _read_frame(self):
        # Read header
        header = self.socket.read(2)
        if not header:
            raise Exception('Connection closed')
            
        fin = header[0] & 0x80
        opcode = header[0] & 0x0f
        masked = header[1] & 0x80
        length = header[1] & 0x7f
        
        if length == 126:
            length = int.from_bytes(self.socket.read(2), 'big')
        elif length == 127:
            length = int.from_bytes(self.socket.read(8), 'big')
            
        if masked:
            mask = self.socket.read(4)
            data = bytearray(self.socket.read(length))
            for i in range(length):
                data[i] ^= mask[i % 4]
        else:
            data = self.socket.read(length)
            
        return opcode, data 