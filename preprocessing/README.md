First, download the [raw data files](https://www.microsoft.com/en-us/download/details.aspx?id=100121)
and place the JSON files in a folder `data`

Then, generate an SQLite database based on the JSON data files:
```bash
python3 generate-all-data.py
```

Generate a subset of that data with the signs that you want included in the dataset:
```bash
python3 generate-initial-data.py all-data.db initial-data.db eat nice want teacher orange white what like friend fish yes where no milk deaf
```

Generate a folder structure with the videos from the initial dataset:
```bash
python3 generate-videos.py initial-data.db
```
