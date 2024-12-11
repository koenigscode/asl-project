# Video preprocessing

The [raw dataset](https://www.microsoft.com/en-us/download/details.aspx?id=100121)
consists of JSON files that provide the URLs to the videos of people signing words.

To make use of this data, we put them into a SQLite database and then download the videos.

You can either download the already processed videos based on the inital dataset (trimmed and cropped)
from Google Drive, or create an initial dataset and tranform it into videos yourself, using the scripts
in this folder.

## Downloading the processed videos
You can download the initial dataset as videos from
[Google Drive](https://drive.google.com/drive/folders/1YkB6lUdzNHrJiLRgTl1Rz6n8tOnmhCg_?usp=sharing).


## Pre-processing the videos locally
If you want a different initial dataset or want to run the scripts on your own,
follow these steps:


First, download the [raw data files](https://www.microsoft.com/en-us/download/details.aspx?id=100121)
and place the JSON files in a folder `data`

Then, generate an SQLite database based on the JSON data files:
```bash
python3 generate-all-data.py
```

Generate a subset of that data with the signs that you want included in the dataset:
```bash
python3 generate-initial-data.py all-data.db initial-data.db eat no teacher want fish
```

Generate a folder structure with the videos from the initial dataset, and set the fps:
```bash
python generate-videos.py initial-data.db 24
```
