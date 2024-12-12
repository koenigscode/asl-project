# A Sign from Above

## Getting started
### Setting up the dataset
Make sure you have the folder `processing/datasets`, which contains the files from
[Google Drive](https://drive.google.com/drive/folders/1cV8PywmyJMYZQgGM-fDWff11nkbltyfy?usp=sharing).

`datasets` should directly contain the folders 'from-adam', 'from-david', etc

Then, merge the datasets into one dataset:
```bash
cd processing
python merge-folders.py datasets/top*/* datasets/from-*
```

Depending on your installation, you might need to use `python3` instead of `python`.
If you're in a conda environment, `python` should be fine.

This created the folder `processing/dataset-merged`.

If you want to use different words for training, or want to use a different dataset, you can look at [processing/README.md](./processing/README.md).

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
- `processing`: Scripts for downloading videos from the original dataset, cropping them, changing the fps,
    cutting them and merging dataset folders. You should have downloaded the datasets folder into this folder.
- `server`: Django server for the app
    - `server/app`: Main app folder
    - `server/app/templates`: HTML templates
    - `server/static`: Static files (Videos to show on frontend). Will be collected to `server/staticfiles` during the Docker build, and served with whitenoise.
    - `server/Dockerfile` Dockerfile for Django - for development, use `docker-compose.yml` instead
