# A Sign from Above


## Project Description
This application helps users practice signing words in ASL.

The user is presented with how the words are signed,
and has to sign the prompted word to practice their newly acquired knowledge.

The user can choose whether they want to see an instruction video on how to sign a word, or if they want to practice without any help.
The app then gives feedback on whether the word was signed correctly or not.

The goal of this system is to be an educational tool that can be used to increase ASL literacy by providing an easy to use environment for learning.


## Getting started
### Setting up the dataset
Make sure you have the folder `preprocessing/datasets`, which contains the files from
[Google Drive](https://drive.google.com/drive/folders/1cV8PywmyJMYZQgGM-fDWff11nkbltyfy?usp=sharing).

`datasets` should directly contain the folders 'from-adam', 'from-david', etc

Then, merge the datasets into one dataset:
```bash
cd preprocessing
python merge-folders.py datasets/top*/* datasets/from-*
```

Depending on your installation, you might need to use `python3` instead of `python`.
If you're in a conda environment, `python` should be fine.

This created the folder `preprocessing/dataset-merged`.

If you want to use different words for training, or want to use a different dataset, you can look at [preprocessing/README.md](./preprocessing/README.md).

### Training the model
Open [model_training/asl_pipeline.ipynb](./model_training/asl_pipeline.ipynb) in Jupyter Notebook and execute everything.
This generates the files `models/<MODEL_NAME>.keras` and `models/<MODEL_NAME>.env` -
the env file contains information for using the models, e.g. on which video fps the model was trained.

### Running the app
In the repository root folder, run:
```bash
docker compose up
```

The container will automtically reload the app if you change the `/server` code

If you have run the container before, but some dependencies or `/server/static` files have changed, you have to re-build it:
```bash
docker compose up --build
```

The app is now available at the port specified in [docker-compose.yml](./docker-compose.yml).

If `SAVE_RECORDINGS=True` in [docker-compose.yml](./docker-compose.yml), the recordings from the end-users
will be saved in the `/recordings` folder.
They can be used for further training later on.
Only videos where hand landmarks were detected are saved.


## Folder structure
- `model_training`: Jupyter Notebook for training the model, landmark detection script
- `models`: Trained models, `.env` file for model metadata, landmark detection model
- `preprocessing`: Scripts for downloading videos from the original dataset, cropping them, changing the fps,
    cutting them and merging dataset folders. You should have downloaded the datasets folder into this folder.
- `server`: Django server for the app
    - `server/app`: Main app folder
    - `server/app/templates`: HTML templates
    - `server/static`: Static files (Videos to show on frontend). Will be collected to `server/staticfiles` during the Docker build, and served with whitenoise.
    - `server/Dockerfile` Dockerfile for Django - for development, use `docker-compose.yml` instead


## Attendance table

Here, we tracked our meetings every week, as well as the attendance of each member to those meetings.
An 'x' marks that the person was present, a '/' marks a tardy, and a ' ' marks an absence.

| Week | Date           | Adam | Parisa | Kale | Sofia | David | Teo | Notes                                          |
| ---- | -------------- | ---- | ------ | ---- | ----- | ----- | --- | ---------------------------------------------- |
| 45   | Nov 8th, 2024  | x    | x      | x    | x     | x     | x   |                                                |
| 46   | Nov 11th, 2024 | x    | x      | x    | x     | x     | x   |                                                |
| 46   | Nov 14th, 2024 | x    | x      | x    | x     | x     | x   |                                                |
| 47   | Nov 19th, 2024 | x    | x      | x    | x     | x     | x   |                                                |
| 47   | Nov 21th, 2024 | x    | x      | x    | x     | x     | x   |                                                |
| 47   | Nov 22nd, 2024 | x    | x      | x    | x     | /     | x   |                                                |
| 48   | Nov 28th, 2024 | x    | x      | x    | x     | x     | x   |                                                |
| 48   | Nov 29th, 2024 | x    | x      | x    | x     | x     | x   |                                                |
| 49   | Dec 5th, 2024  | x    | x      | x    | x     | x     | x   |                                                |
| 49   | Dec 6th, 2024  | x    | x      | x    | x     | /     | x   |                                                |
| 50   | Dec 12th, 2024 | x    | x      | x    | x     |       | x   | David had a full day event for another course  |
| 50   | Dec 13th, 2024 | x    | x      | x    | x     | x     | x   |                                                |
| 51   | Dec 20th, 2024 | x    | x      | x    | x     | x     | x   |                                                |
| 51   | Dec 21st, 2024 | x    | x      | x    | x     | x     | x   |                                                |
| 52   | Dec 26th, 2024 | x    | x      | x    | x     | x     | x   |                                                |
| 52   | Dec 27th, 2024 | x    | x      | x    | x     | x     |     | Teo wasn't available due to other appointments |
| 1    | Jan 2nd, 2025  | x    | x      | x    | x     | x     | x   |                                                |
| 1    | Jan 3rd, 2025  | x    | x      | x    | x     | x     | x   |                                                |

