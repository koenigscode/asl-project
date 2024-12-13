import shutil
import argparse
import os

output_dir = "dataset-merged"

parser = argparse.ArgumentParser(
    description="Merge recording datasets into one directory.")
parser.add_argument("recordings", nargs='+',
                    help="List of recording directories to merge")
args = parser.parse_args()

os.makedirs(output_dir, exist_ok=False)

for recording_dir in args.recordings:
    if not os.path.exists(output_dir):
        print("Output folder doesn't exist")
        exit(1)

    shutil.copytree(recording_dir, output_dir, dirs_exist_ok=True)
