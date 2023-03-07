import time
import socket
import stable_whisper
import torch
import multiprocessing


def task(queue, x, y):
    cuda = torch.cuda.is_available()

    if cuda:
        print("CUDA is available.")
    else:
        print("CUDA not available.")


    print("Loading model.")
    model = stable_whisper.load_model('medium')
    print("Loaded model.")

    time.sleep(5)
    queue.put(x + y)

SOCKET_BACKLOG = 0
BIND_HOST = '192.168.0.1'

sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((BIND_HOST, 49152))
sock.listen(SOCKET_BACKLOG)


queue = multiprocessing.Queue()

print("Accepting connections")
while True:
    conn, address = sock.accept()
    print(conn)
    print(address)
    bytestr = conn.recv(1024)
    conn.close()

    commandstr = bytestr.decode('utf8')

    parts = commandstr.split()

    if not parts:
        raise Exception('bad')

    command = parts[0]

    if command == 's':
        process = multiprocessing.Process(target=task, args=(queue, 1,2))
        process.start()
        print("Created whisper process with pid", process.pid)
    elif command == 'q':
        value = queue.get()
        print("value from queue was", value)
    else:
        raise Exception('no')
    
conn.close()
sock.close()





