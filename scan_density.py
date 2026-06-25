import pysrt
import re
import psycopg2
import configparser
import subprocess
import sys
import operator
from typing import Optional


COMMAND = ("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1")

def get_duration(path) -> Optional[float]:
    try:
        bval = subprocess.check_output(COMMAND + (path,))
        cleaned = bval.decode('utf-8').rstrip()
        return float(cleaned)
    except subprocess.CalledProcessError as e:
        return None
    except ValueError as e:
        return None

def get_items(config):
    conn_args = {
        'host': config.get('main', 'db_hostname'),
        'dbname': config.get('main', 'db_name'),
        'user': config.get('main', 'db_username'),
        'password': config.get('main', 'db_password')
    }

    conn = psycopg2.connect(**conn_args)
    cur = conn.cursor()

    cur.execute("SELECT pathname, subtitles FROM item")
    qry_result = cur.fetchall()
    cur.close()
    conn.close()
    return qry_result

config = configparser.ConfigParser()
    
with open('whisper-frontend.ini') as f:
    config.read_file(f)

items = get_items(config)

for pathname, subtitles in items:
    if 'Y:/yar' in pathname:
        x = re.sub(r'Y:/yar/', '/mnt/nfs/yar/', pathname)
        dur = get_duration(x)
        if not dur:
            raise Exception('no duration')
        
        if dur <= 0:
            raise Exception('bad duration')

        parsed = pysrt.from_string(subtitles)
        count = 0
        for item in parsed:
            #     # main are start, end position text
            count += len(item.text.split())

        density = count / dur
        print(f'{x},{density}')       
