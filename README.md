# File Synchronizer

A program that synchronizes two folders: source and
replica. The program maintains a full, identical copy of source
folder at replica folder. The synchronization is done periodically.

## Dependencies

Make sure that Python 3.12 is installed in your system.

https://www.python.org/downloads/

## How to run

The main script is located at `sync_file/main.py`

In order to run the program, you need to provide a path for the source folder and a path for the replica folder. Both of these directories must exist.

Example:

`python3.12 sync_file/main.py source dest` (For Linux/MacOS)

`python3.12 sync_file\main.py source dest` (For Windows)

Optionally, the synchronization interval, in seconds, and the path for the log files, can also be provided. If not provided, the sync interval will be 60 seconds by default, and the log-file-path will be log.txt, inside the current working directory.

Example:

`python3.12 sync_file/main.py source dest 180 home/user/logs`

Some sample directories with sub-directories, text and video files are included for demonstration purposes.
