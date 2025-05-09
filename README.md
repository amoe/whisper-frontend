# whisper-frontend

The purpose of this server is to run on a physical hardware device (probably
with a GPU) and listen for transcription jobs.

This *requires* Python >= 3.9 on the host machine, specifically on Windows.

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

## Radar

Apparently there are newer and faster versions of Whisper now that allow using
the newer whisper models such as `large-v2` and `large-v3`.  These models can be
used with lower amounts of VRAM on the host machine, using faster engines such
as `faster-whisper`, and `whisperx` might bundle some of the correction
capabilities.  It's impractical to evaluate the respective behaviours of these
solutions for me at the moment.

## Windows Install

I recommend using "Terminal" rather than the stock Windows command prompt
program.

Download the source code to `~/whisper-frontend`, the full path will look
something like `C:\Users\amoeb\Documents\whisper-frontend`.

Create a venv locally under a `venv` subdirectory and install dependencies into
this.  The dependencies are quite simple and can be installed using pip.

It's possible to deploy this on Windows using the following method:

* Press `Win+R` to load the Run dialog
* `shell:startup`
* This will take you to the Startup folder

Do this after installing the software to a venv using Poetry
