import psycopg2
import configparser
import sys

def list(config):
    conn_args = {
        'host': config.get('main', 'db_hostname'),
        'dbname': config.get('main', 'db_name'),
        'user': config.get('main', 'db_username'),
        'password': config.get('main', 'db_password')
    }

    conn = psycopg2.connect(**conn_args)
    cur = conn.cursor()

    cur.execute("SELECT pathname FROM item")

    qry_result = cur.fetchall()


    for x in qry_result:
        print(x[0])
    

    cur.close()
    conn.close()


config = configparser.ConfigParser()
    
with open('whisper-frontend.ini') as f:
    config.read_file(f)

list(config)

