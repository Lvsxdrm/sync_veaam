### Parameters
#- `source`: Path to the source directory.
#- `replica`: Path to the replica directory.
#- `--interval`: Time in seconds between synchronization checks. Default is 60.
#- `--log`: Path to the log file.

## Requirements
#Python 3.6+

## Author
#[Kaussar Dilmurat]


import argparse
import logging
import time
from pathlib import Path
import shutil
import hashlib

#set up command-line argument parsing
parser = argparse.ArgumentParser(description='Synchronize two directories.')
parser.add_argument('source', help='The source directory to sync from')
parser.add_argument('replica', help='The replica directory to sync to')
parser.add_argument('--interval', type=int, default=60, help='The interval in seconds between sync checks')
parser.add_argument('--log', default='sync.log', help='Path to the log file')

#parse arguments
args = parser.parse_args()

#set up logging
logging.basicConfig(filename=args.log, level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Function to compute MD5 checksum for a file
def md5_checksum(file_path):
    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)
        return file_hash.hexdigest()

#function to sync the dirs   
def sync_dirs(source, replica):
    try:
        source_path = Path(source)
        replica_path = Path(replica)
        replica_path.mkdir(parents=True, exist_ok=True)

        source_files = {file.relative_to(source_path): file for file in source_path.rglob('*') if file.is_file()}
        replica_files = {file.relative_to(replica_path): file for file in replica_path.rglob('*') if file.is_file()}

        for relative_path, file in source_files.items():
            replica_file = replica_path / relative_path
            if not replica_file.exists() or md5(file) != md5(replica_file):
                replica_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, replica_file)
                logging.info(f'File copied/updated: {file} -> {replica_file}')

        for relative_path, file in replica_files.items():
            if relative_path not in source_files:
                file.unlink()
                logging.info(f'File removed from replica: {file}')

    except Exception as e:
        logging.error(f"Error during sync operation: {str(e)}")

#function to calculate MD5 checksum
def md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

#main loop
while True:
    sync_dirs(args.source, args.replica)
    time.sleep(args.interval)