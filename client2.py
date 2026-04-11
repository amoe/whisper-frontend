from xmlrpc.client import ServerProxy
import sys
import tomllib
from pathlib import Path


# A simple client to submit a single job.

config_path = Path.home() / '.config' / 'whisper-frontend-client-config.toml'

with open(config_path, 'rb') as f:
    config = tomllib.load(f)

remote_host = config['main']['remote_host']
remote_port = config['main']['remote_port']

path = sys.argv[1]
lang = sys.argv[2]

with ServerProxy(f'http://{remote_host}:{remote_port}/') as proxy:
    proxy.start_job(path, lang)


