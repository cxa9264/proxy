import socket
import selectors
import struct

class SocksProxy:

    def __init__(self, addr, port):
        
        self.addr = addr
        self.port = port

        self.conn_pool = []

        # create and bind socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.addr, self.port))
        self.server.listen(10)
        print("Socks server listening on port: {}".format(self.port))
        
        # register socket to selector
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.server, selectors.EVENT_READ, self.connect_single)
    
    def connect_single(self, s):
        
        conn, addr = s.accept()
        print("Accepted", conn, 'from', addr)

        conn.setblocking(False)

        # self.process_connect(conn)

        self.selector.register(conn, selectors.EVENT_READ, self.process_connect)

    def process_connect(self, conn):
        
        print(conn.recv(20))
        return

        # read first two bytes
        ver, methods = conn.recv(1), conn.recv(1)
        methods = conn.recv(ord(methods))

        # reply : version 5, no auth
        conn.send(b"\x05\x00")

        # read request
        ver, cmd, rsv, atype = conn.recv(1), conn.recv(1), conn.recv(1), conn.recv(1)

        # only 0x01 supported for cmd
        if ord(cmd) != 1:
            conn.close()
            return
        
        # only ipv4 supported for atype
        if ord(atype) == 1:
            # ip v4
            remote_addr = socket.inet_ntoa(conn.recv(4)) # convert ip to . division form
            remote_port = struct.unpack(">H", conn.recv(2))[0]
        elif ord(atype) == 3:
            # domain name
            addr_len = ord(conn.recv(1))
            remote_addr = conn.recv(addr_len)
            remote_port = struct.unpack(">H", conn.recv(2))[2]
        else:
            # unsupported type
            # reply: ver 5, rep add type not supported, rsv, atype ipv4, addr 0.0.0.0, port 2222
            reply = b"\x05\x08\x00\x01" + socket.inet_aton("0.0.0.0") + struct.pack(">H", 2222)
            conn.send(reply)
            conn.close()
            return
        
        print("cmd: {0} target ---> {1}:{2}".format(cmd, remote_addr, remote_port))

        # connect dest
        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if remote.connect((remote_addr, remote_port)) != 0:
            reply = b"\x05\x05\x00\x01" + socket.inet_aton("0.0.0.0") + struct.pack(">H", 2222)
            conn.send(reply)
            conn.close()
            return

        # reply connect establish
        reply = b"\x05\x00\x00\x01" + socket.inet_aton("0.0.0.0") + struct.pack(">H", 2222)
        conn.send(reply)

        return

    def connect_forever(self):
        while True:
            datas = self.selector.select()
            for key, event in datas:
                callback = key.data
                callback(key.fileobj)

if __name__ == "__main__":

    socket_proxy = SocksProxy('localhost', 22700)
    socket_proxy.connect_forever()
