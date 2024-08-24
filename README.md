# whisper-frontend

The purpose of this server is to run on a physical hardware device (probably
with a GPU) and listen for transcription jobs.

This *requires* Python >= 3.9 on the client, specifically on Windows.

To use the scripts, create a file containing your database credentials, named
'whisper-frontend.ini'.  It should look like this:

    [main]
    bind_host = localhost
    output_dir = /home/amoe
    db_name = whisper_frontend
    db_username = whisper_frontend
    db_password = xyzzy
    db_hostname = somehost

The server will use these credentials to write completed transcription jobs to
the given PostgreSQL database.
