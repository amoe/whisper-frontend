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

sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('localhost', 49152))
sock.listen(SOCKET_BACKLOG)

commands = {
    b's': 'start',
    b'q': 'query'
}

queue = multiprocessing.Queue()

print("Accepting connections")
while True:
    conn, address = sock.accept()
    print(conn)
    print(address)
    bytestr = conn.recv(1)
    conn.close()
    print(bytestr)

    action = commands[bytestr]

    if action == 'start':
        process = multiprocessing.Process(target=task, args=(queue, 1,2))
        process.start()
        print("Created whisper process with pid", process.pid)
    elif action == 'query':
        value = queue.get()
        print("value from queue was", value)
    else:
        raise Exception('no')
    
conn.close()
sock.close()





