import time
import socket
import stable_whisper
import torch
import configparser
import uuid
import os
from multiprocessing import Pool, Manager


def fprint(*args, **kwargs):
    print(*args, **kwargs, flush=True)


def task(input_path, output_dir, job_id):
    fprint("Launched task with process", os.getpid())
    return {'success': True}
    output_dir = '/srv/cifs_rw/whisper_transcriptions'
    unique_filename = str(job_id) + '.srt'
    output_path = os.path.join(output_dir, unique_filename)
    cuda = torch.cuda.is_available()

    if cuda:
        fprint("CUDA is available.")
    else:
        fprint("CUDA not available.")

    fprint("Loading model.")
    model = stable_whisper.load_model('medium')   # loopkever can only use small
    fprint("Loaded model.")

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
    result = {'success': True}
    return result

def error_callback(e):
    raise e

def ready_callback(v):
    fprint("Ready callback with value", v)


def serve_forever(sock, pool: Pool, config):
    jobs = {}
    while True:
        conn, address = sock.accept()
        print(conn)
        print(address)
        bytestr = conn.recv(1024)
        conn.close()

        commandstr = bytestr.decode('utf8').rstrip()

        parts = commandstr.split(maxsplit=1)

        if not parts:
            raise Exception('bad')

        command = parts[0]

        if command == 's':
            job_id = uuid.uuid4()
            args = (parts[1], config.get('main', 'output_dir'), job_id)
            fprint("Calling with args", args)
            res = pool.apply_async(task, args=args, callback=ready_callback, error_callback=error_callback)
            fprint("Created task, got async result", res)
            jobs[job_id] = res
            # we don't do anything with the result for now and keep relying
            # on the queue to pass results, yet pool can actually return the
            # result
        elif command == 'q':
            the_job = list(jobs.keys())[0]
            fprint("querying job", the_job)
            value = jobs[the_job].get()
            print("value from queue was", value)
            del jobs[the_job]
        else:
            raise Exception('no')


def main():
    config = configparser.ConfigParser()
    
    with open('whisper-frontend.ini') as f:
        config.read_file(f)
    
    SOCKET_BACKLOG = 0
    BIND_HOST = '192.168.0.1'

    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((config.get('main', 'bind_host'), 49152))
    sock.listen(SOCKET_BACKLOG)

    
    print("Accepting connections")
    with Pool(processes=1) as pool:
        serve_forever(sock, pool, config)
        
    sock.close()

# Beware that the main method MUST be guarded with this on windows, otherwise
# subprocess will hang without any message
if __name__ == '__main__':
    main()
