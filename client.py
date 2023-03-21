from xmlrpc.client import ServerProxy
import sys

with ServerProxy('http://elang:49152/') as proxy:
    with open('/home/amoe/rikerpaths') as f:
        for line in f:
            name = line.rstrip()
            proxy.start_job(name)



