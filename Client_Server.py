import threading
import socket
import json
import struct
from datetime import datetime
 
semaforo_desligar = threading.Event()
 
def parse_pack(pack):
    raw_pack = pack.decode()
    return json.loads(raw_pack)
 
def create_pack(username, message):

    date = datetime.now().isoformat()

    pack = {
        'dt' : date,
        'msg' : message,
        'autor': username,
    }
    raw_pack = json.dumps(pack)
    return raw_pack.encode()
 
 
def server():
    print('Starting server...')
    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM,
        socket.IPPROTO_UDP,
    )
    sock.settimeout(0.5)
    sock.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1,
    )
    mreq = struct.pack(
        '4sl',
        socket.inet_aton('224.1.1.1'),
        socket.INADDR_ANY,
    )
    sock.setsockopt(
        socket.IPPROTO_IP,
        socket.IP_ADD_MEMBERSHIP,
        mreq,
    )
    sock.bind(('224.1.1.1', 5007,))
 
    while not semaforo_desligar.is_set():
        try:
            pack = parse_pack(sock.recv(10240))
            dt = datetime.fromisoformat(pack['dt'])
            print(f'{pack["autor"]} / {dt.strftime("%H:%M")}: {pack["msg"]} ')
        except TimeoutError:
            pass
 
sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM,
    socket.IPPROTO_UDP,
)
 
sock.setsockopt(
    socket.IPPROTO_IP,
    socket.IP_MULTICAST_TTL,
    2,
)
 
server_thread = threading.Thread(
    target=server,
)
 
username = input("Username:")

server_thread.start()
 
try:
    while True:
        text = input()
        pack = create_pack(username, text)
        sock.sendto(pack, ('224.1.1.1', 5007))
except KeyboardInterrupt:
    print('desligando...')
    semaforo_desligar.set()
    server_thread.join()