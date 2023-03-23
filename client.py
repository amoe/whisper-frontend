from xmlrpc.client import ServerProxy
import sys

with ServerProxy('http://elang:49152/') as proxy:
    with open('/home/amoe/rikerpaths') as f:
        lines = f.readlines()
        for line in lines:
            name = line.rstrip()
            proxy.start_job(name)



