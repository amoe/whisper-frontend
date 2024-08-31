from xmlrpc.client import ServerProxy
import sys

REMOTE_HOST = 'localhost'
REMOTE_PORT = 49152

with ServerProxy(f'http://{REMOTE_HOST}:{REMOTE_PORT}/') as proxy:
    proxy.start_job(sys.argv[1], sys.argv[2])


