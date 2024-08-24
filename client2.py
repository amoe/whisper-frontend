from xmlrpc.client import ServerProxy
import sys

with ServerProxy('http://elang:49152/') as proxy:
    proxy.start_job(sys.argv[1], sys.argv[2])


