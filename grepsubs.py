import pysrt
import re
import psycopg2
import configparser
import sys

def slurp_subtitles(config):
    conn_args = {
        'host': config.get('main', 'db_hostname'),
        'dbname': config.get('main', 'db_name'),
        'user': config.get('main', 'db_username'),
        'password': config.get('main', 'db_password')
    }

    conn = psycopg2.connect(**conn_args)
    cur = conn.cursor()

    cur.execute("SELECT subtitles, pathname FROM item")

    qry_result = cur.fetchall()

    cur.close()
    conn.close()

    return qry_result


config = configparser.ConfigParser()

with open('whisper-frontend.ini') as f:
    config.read_file(f)

requested = sys.argv[1]
print("Loading subs")
results = slurp_subtitles(config)
print("Loaded", len(results), "subs")

for subtitles, pathname in results:
    print(pathname)
    parsed = pysrt.from_string(subtitles)

    for item in parsed:
        #     # main are start, end position text
        item_text = item.text
        # xxx regex escaping?
        if re.search(requested, item_text):
            print(f'{pathname}: {item_text}')           
