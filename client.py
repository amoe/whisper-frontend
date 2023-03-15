from xmlrpc.client import ServerProxy

with ServerProxy('http://localhost:49153/') as proxy:
    print(proxy.start_job('test.mkv'))
