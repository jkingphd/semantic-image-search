# semantic-image-search
Demonstration application for 2023 Nashville Analytics Summit - Do I really need a vector database?

## Environment

The environment file is defined in environment.yml and is intended to be used with [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/). Run the following to automatically create a new environment named vectordb.

`conda env create -f environment.yml`

You will also need to install [Docker](https://docs.docker.com/get-docker/) and Docker Compose to spin up Milvus.

## Data

### Getting the images

This application makes use of [The Unsplash Dataset](https://github.com/unsplash/datasets), although any large set of images can be used. For the demo application, I requested and gained access to the full dataset of 4.8M images, although I only used 500K due to the size of the dataset. The lite dataset (25K images) is freely available from [Unsplash](https://unsplash.com/data/lite/latest) and on [Kaggle](https://www.kaggle.com/datasets/anandaramg/unsplash-image-download-data). You will need to download these files directly from Unsplash and extract the photo index file into the data/: This can be done from the command line in Linux as follows:

```
mkdir data
wget https://unsplash.com/data/lite/latest -O data/unsplash-lite.zip
unzip -d data/ data/unsplash-lite.zip photos.tsv000
```

These datasets do not contain the images, you will need to scrape them from the links provided in the photos reference table using 1-pull-images.ipynb. This will create a directory in data/ named unsplash-raw/ and download the images. Note that these images are quite large—even the lite dataset takes up ~75GB of disk space.

### Resizing the images

Once downloaded, use 2-resize-images.ipynb to resize the raw images to a max dimension of 512 pixels (while maintaining the original aspect ratio). This will make things more manageable for the encoding step. We'll also search these resized images in the webapp, rather than the full size images, to save on bandwidth.

### Encoding the images

## Vector Database

### Setting up Milvus

### Setting up Attu (optional)

## Streamlit

At this point, you should be able to run the application. If you created a user for this application (highly suggested), set the environmental variables in the shell before running the below command or [modify the secrets file in your local streamlit install](https://docs.streamlit.io/library/advanced-features/secrets-management).

`streamlit run --server.port 8081 --server.maxUploadSize 10 --browser.gatherUsageStats false ss-milvus.py`

Feel free to change the port or upload limit. `--browser.gatherUsageStats false` simply deactivates telemetry.