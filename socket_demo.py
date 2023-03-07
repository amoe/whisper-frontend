import time
import socket
import multiprocessing


def task(queue, x, y):
    time.sleep(5)
    
    queue.put(x + y)

SOCKET_BACKLOG = 0

sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('localhost', 49152))
sock.listen(SOCKET_BACKLOG)

commands = {
    b's': 'start',
    b'q': 'query'
}

queue = multiprocessing.Queue()

while True:
    conn, address = sock.accept()
    print(conn)
    print(address)
    bytestr = conn.recv(1)
    print(bytestr)

    action = commands[bytestr]

    if action == 'start':
        process = multiprocessing.Process(target=task, args=(queue, 1,2))
        process.start()
    elif action == 'query':
        value = queue.get()
        print("value from queue was", value)
    else:
        raise Exception('no')
    
    conn.close()
conn.close()
sock.close()





