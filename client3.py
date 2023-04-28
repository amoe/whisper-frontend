from xmlrpc.client import ServerProxy
import configparser
import psycopg2

def fetch_transcribed(config):
    conn_args = {
        'host': config.get('main', 'db_hostname'),
        'dbname': config.get('main', 'db_name'),
        'user': config.get('main', 'db_username'),
        'password': config.get('main', 'db_password')
    }

    conn = psycopg2.connect(**conn_args)
    cur = conn.cursor()

    cur.execute("SELECT pathname FROM item",)

    result = [x[0] for x in cur.fetchall()]
    cur.close()
    conn.close()

    return result


config = configparser.ConfigParser()
    
with open('whisper-frontend.ini') as f:
    config.read_file(f)

transcribed = set(fetch_transcribed(config))
    
with open('/home/amoe/rikerpaths') as f:
    lines = set([l.rstrip() for l in f.readlines()])


diff = lines.difference(transcribed)
print(len(transcribed))
print(len(lines))
print(len(diff))


with ServerProxy('http://elang:49152/') as proxy:
    for path in diff:
        proxy.start_job(path, 'fr')
