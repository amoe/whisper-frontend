import uuid
import stable_whisper
import torch
import os
import configparser
import multiprocessing
from xmlrpc.server import SimpleXMLRPCServer

def fprint(*args, **kwargs):
    print(*args, **kwargs, flush=True)

def error_callback(e):
    raise e

def ready_callback(v):
    fprint("Ready callback with value", v)


def task(input_path, output_dir, job_id):
    fprint("Launched task with process", os.getpid())
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


class JobServer:
    def __init__(self, pool, config):
        self.pool = pool
        self.config = config
        self.jobs = {}
    
    def add(self, x, y):
        return x + y

    def start_job(self, input_path):
        job_id = uuid.uuid4()
        args = (input_path, self.config.get('main', 'output_dir'), job_id)
        fprint("Calling with args", args)
        res = self.pool.apply_async(task, args=args, callback=ready_callback, error_callback=error_callback)
        fprint("Created task, got async result", res)
        self.jobs[job_id] = res
        return True

    
def main():
    # Force unix systems to use the more limited spawn API, to more closely
    # match Windows.
    context = multiprocessing.get_context('spawn')
    config = configparser.ConfigParser()
    
    with open('whisper-frontend.ini') as f:
        config.read_file(f)

    server = SimpleXMLRPCServer(addr=(config.get('main', 'bind_host'), 49152))
    with context.Pool(processes=1) as pool:
        instance = JobServer(pool, config)
        server.register_instance(instance)
        print("Accepting connections")
        server.serve_forever()
        

if __name__ == '__main__':
    main()
