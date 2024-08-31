import uuid
import whisper
import stable_whisper
import torch
import os
import configparser
import multiprocessing
import psycopg2
from xmlrpc.server import SimpleXMLRPCServer

WHISPER_MODEL = 'medium'

def fprint(*args, **kwargs):
    print(*args, **kwargs, flush=True)

def error_callback(e):
    raise e

def ready_callback(v):
    fprint("Ready callback with value", v)



def task(
    input_path, lang_code: str, output_dir, job_id, db_name, db_username, db_password, db_hostname
):
    fprint("Launched task with process", os.getpid())
    unique_filename = str(job_id) + '.srt'
    output_path = os.path.join(output_dir, unique_filename)
    cuda = torch.cuda.is_available()

    if cuda:
        fprint("CUDA is available.")
    else:
        fprint("CUDA not available.")

    fprint("Loading model.")
    model = stable_whisper.load_model(WHISPER_MODEL)   # loopkever can only use small
    fprint("Loaded model.")

    no_speech_threshold = 0.7
    compression_ratio_threshold = 1.7
    beam_size = 4
    best_of = 3
    temperature = 0.0

    result = model.transcribe(
        input_path, language=lang_code, verbose=False,
        condition_on_previous_text=False,
        no_speech_threshold=no_speech_threshold,
        compression_ratio_threshold=compression_ratio_threshold,
        beam_size=beam_size,
        best_of=best_of,
        temperature=temperature
    )

    
    # These options disable all 'fancy' stuff for subtitles, e.g. colouring
    # per-word.  This loses some information but makes sure the subtitles remain
    # plain-text which makes them easy to search.
    result.to_srt_vtt(output_path, vtt=False, segment_level=True, word_level=False)
    with open(output_path, 'r', encoding='utf-8') as f:
        srt_content = f.read()

    conn = psycopg2.connect(host=db_hostname, dbname=db_name, user=db_username, password=db_password)
    conn.set_client_encoding('UTF8')
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO item (pathname, completed_date, subtitles) VALUES (%s, CURRENT_DATE, %s)",
        (input_path, srt_content)
    )
    conn.commit()
    cur.close()
    conn.close()

    result = {'success': True}
    return result


class JobServer:
    def __init__(self, pool, config):
        self.pool = pool
        self.config = config
        self.jobs = {}
    
    def add(self, x, y):
        return x + y

    def start_job(self, input_path, lang_code: str):
        job_id = uuid.uuid4()
        args = (
            input_path,
            lang_code,
            self.config.get('main', 'output_dir'),
            job_id,
            self.config.get('main', 'db_name'),
            self.config.get('main', 'db_username'),
            self.config.get('main', 'db_password'),
            self.config.get('main', 'db_hostname')
        )
        fprint("Calling with args", args)
        res = self.pool.apply_async(task, args=args, callback=ready_callback, error_callback=error_callback)
        fprint("Created task, got async result", res)
        self.jobs[job_id] = res
        return True

    
def main():
    print("Whisper version:", whisper.__version__)
    print("Whisper model:", WHISPER_MODEL)
    print("Launched with stable-whisper version:", stable_whisper.__version__)
    
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
        try:
            server.serve_forever()
        except KeyboardInterrupt as e:
            print("Shutting down.")
            pool.terminate()
            pool.close()
            pool.join()


if __name__ == '__main__':
    main()
