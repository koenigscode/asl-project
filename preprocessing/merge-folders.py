# Created with help of ChatGPT.
# https://chatgpt.com/share/675abc48-38e4-8006-acee-4f85a5afb79f

import shutil
import argparse
import os

parser = argparse.ArgumentParser(
    description="Merge recording datasets into one directory.")
parser.add_argument("recordings", nargs='+',
                    help="List of recording directories to merge")
args = parser.parse_args()

# Create the target directory (dataset-merged)
output_dir = "dataset-merged"
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)  # Remove it if it already exists
shutil.copytree("dataset", output_dir, dirs_exist_ok=True)

# Merge the specified recording directories
for recording_dir in args.recordings:
    target_dir = os.path.join(output_dir, "train")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    # Copy the recording data into the 'train' folder of the merged dataset
    shutil.copytree(recording_dir, target_dir, dirs_exist_ok=True)

print("Dataset merge complete.")
