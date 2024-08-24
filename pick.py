import psycopg2
import configparser
import sys

def get_filename(config):
    conn_args = {
        'host': config.get('main', 'db_hostname'),
        'dbname': config.get('main', 'db_name'),
        'user': config.get('main', 'db_username'),
        'password': config.get('main', 'db_password')
    }

    conn = psycopg2.connect(**conn_args)
    cur = conn.cursor()

    
    cur.execute("SELECT pathname FROM item ORDER BY RANDOM() LIMIT 5")

    qry_result = cur.fetchone()

    if qry_result:
        item = qry_result[0]
    else:
        item = None
        

    cur.close()
    conn.close()

    return item


config = configparser.ConfigParser()
    
with open('whisper-frontend.ini') as f:
    config.read_file(f)

filename = get_filename(config)
if filename is None:
    raise Exception(f'subs not found for item: {requested!r}')
    
    
print(filename)
