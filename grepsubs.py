import pysrt
import re
import psycopg2
import configparser
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", '--ignore-case', action='store_true')
parser.add_argument('-m', '--match-path', action='store', help='only search subtitles where pathname matches the given regex')
parser.add_argument('-l', "--list-matches", action='store_true')
parser.add_argument('-w', '--word', action='store_true', help='treat PATTERN as a whole word')
parser.add_argument('pattern', type=str)
args = parser.parse_args()


def slurp_subtitles(config):
    conn_args = {
        'host': config.get('main', 'db_hostname'),
        'dbname': config.get('main', 'db_name'),
        'user': config.get('main', 'db_username'),
        'password': config.get('main', 'db_password')
    }

    conn = psycopg2.connect(**conn_args)
    cur = conn.cursor()

    cur.execute("SELECT subtitles, pathname FROM item ORDER BY pathname")

    qry_result = cur.fetchall()

    cur.close()
    conn.close()

    return qry_result


config = configparser.ConfigParser()

with open('whisper-frontend.ini') as f:
    config.read_file(f)

if args.word:
    requested = fr'\b{args.pattern}\b'
else:
    requested = args.pattern

print("Loading subs")
results = slurp_subtitles(config)
print("Loaded", len(results), "subs")

for subtitles, pathname in results:
    if args.match_path:
        if not re.search(args.match_path, pathname):
            continue
    
    parsed = pysrt.from_string(subtitles)

    for item in parsed:
        #     # main are start, end position text
        item_text = item.text
        # xxx regex escaping?

        if args.ignore_case:
            flags = re.IGNORECASE
        else:
            flags = 0

        if re.search(requested, item_text, flags):
            if args.list_matches:
                print(pathname)
            else:
                print(f'{pathname}: {item_text}')
