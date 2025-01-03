"""
File: generate-videos.py
Description: Preprocessing script that alters the original dataset into usable data to train the models.

Contributors:
Michael Koenig

Created: 2024-11-19
Last Modified: 2024-12-11

Project: A Sign From Above
URL: https://git.chalmers.se/courses/dit826/2024/group4

License: MIT License (see LICENSE file for details)
"""

from moviepy.video.io.VideoFileClip import VideoFileClip
import hashlib
import sqlite3
import os
import yt_dlp
import argparse
import shutil
from tqdm import tqdm       # Adds progress bars to the console


def download_youtube_video(url, output_path="video.mp4"):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'outtmpl': output_path,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def trim_and_crop_video(input_path, output_path, start_time, end_time, box, video_width, video_height, fps):
    box_y0, box_x0, box_y1, box_x1 = box

    x1 = int(box_x0 * video_width)
    y1 = int(box_y0 * video_height)
    x2 = int(box_x1 * video_width)
    y2 = int(box_y1 * video_height)

    print(f"start_time: {start_time}, end_time: {end_time}")

    video = VideoFileClip(input_path, audio=False).with_subclip(
        start_time, end_time)
    video = video.cropped(x1, y1, x2, y2)

    output_dir = os.path.dirname(output_path)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    video.write_videofile(output_path, fps=min(fps, video.fps), codec='libx264')
    os.remove(input_path)


def generate_random_hash(length=10):
    return hashlib.sha256(os.urandom(16)).hexdigest()[:length]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generates the directory structure with videos")
    parser.add_argument("db", help="Database file")
    parser.add_argument("fps", help="FPS of the output videos", type=int)
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row

    shutil.rmtree("tmp", ignore_errors=True)

    if os.path.exists("dataset"):
        user_input = input(
            "The folder 'dataset' already exists. Press Enter to delete it and continue: ")
        shutil.rmtree("dataset")

    file_counter = {}

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM video_data')

    rows = cursor.fetchall()

    for row in tqdm(rows, desc="Downloading and processing videos", colour="green"):
        data_type = row["data_type"]
        clean_text = row["clean_text"]

        if data_type not in file_counter:
            file_counter[data_type] = {}

        if clean_text not in file_counter[data_type]:
            file_counter[data_type][clean_text] = 0

        hash = generate_random_hash()
        tmp_path = f"tmp/{data_type}/{clean_text}/{hash}.mp4"
        output_path = f"dataset/{data_type}/{clean_text}/{hash}.mp4"

        print(f"Processing {row['url']}")
        try:
            download_youtube_video(row["url"], tmp_path)
            print(f"Downloaded video")

            # Trims and crops the videos based on the parameters outlined in the database
            trim_and_crop_video(
                input_path=tmp_path,
                output_path=output_path,
                start_time=row["start_time"],
                end_time=row["end_time"],
                box=(row["box_1"], row["box_2"], row["box_3"], row["box_4"]),
                video_width=row["width"],
                video_height=row["height"],
                fps=args.fps
            )

        except Exception as e:
            print(f"Error processing video {row['url']} - {e}")

    conn.close()

    shutil.rmtree("tmp")
