import time
import socket
import stable_whisper
import torch
import multiprocessing
import uuid
import os


def task(queue, input_path):
    output_dir = '/srv/cifs_rw/whisper_transcriptions'
    unique_filename = str(uuid.uuid4()) + '.srt'
    output_path = os.path.join(output_dir, unique_filename)
    cuda = torch.cuda.is_available()

    if cuda:
        print("CUDA is available.")
    else:
        print("CUDA not available.")

    print("Loading model.")
    model = stable_whisper.load_model('small')   # loopkever can only use small
    print("Loaded model.")

    no_speech_threshold = 0.7
    compression_ratio_threshold = 1.7
    beam_size = 4
    best_of = 3
    temperature = 0.0

    results = model.transcribe(
        input_path, language='fr', verbose=False,
        condition_on_previous_text=False,
        no_speech_threshold=no_speech_threshold,
        compression_ratio_threshold=compression_ratio_threshold,
        beam_size=beam_size,
        best_of=best_of,
        temperature=temperature
    )

    stable_whisper.results_to_sentence_srt(results, output_path)
    queue.put({'success': True})

    
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

    parts = commandstr.split(maxsplit=1)

    if not parts:
        raise Exception('bad')

    command = parts[0]

    if command == 's':
        process = multiprocessing.Process(target=task, args=(queue, parts[1]))
        process.start()
        print("Created whisper process with pid", process.pid)
    elif command == 'q':
        value = queue.get()
        print("value from queue was", value)
    else:
        raise Exception('no')
    
conn.close()
sock.close()





