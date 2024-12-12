import shutil
import argparse
import os

output_dir = "dataset-merged"

parser = argparse.ArgumentParser(
    description="Merge recording datasets into one directory.")
parser.add_argument("recordings", nargs='+',
                    help="List of recording directories to merge")
args = parser.parse_args()

shutil.copytree("./dataset/train", output_dir, dirs_exist_ok=True)
shutil.copytree("./dataset/val", output_dir, dirs_exist_ok=True)
shutil.copytree("./dataset/test", output_dir, dirs_exist_ok=True)

for recording_dir in args.recordings:
    if not os.path.exists(output_dir):
        print("Output folder doesn't exist")
        exit(1)

    shutil.copytree(recording_dir, output_dir, dirs_exist_ok=True)
