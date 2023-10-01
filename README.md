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

Now that we have the images preprocessed, we'll load the CLIP model and encode in batches of 32. The results are stored in a hdf5 file for future use (insertion) along with the filename.

## Vector Database

### Setting up Milvus

I highly recommend you enable authorization for specify a location to store volumes Milvus (ideally an NVME for performance purposes). This is done by downloading and configuring the following:

- milvus.yaml
    - Change boolean flag for authorizationEnabled from `false` to `true` on line 466 (e.g., `authorizationEnabled: true`).
- docker-compose.yml
    - Change the base path on line 47 from DOCKER_VOLUME_REPOSITY to your desired location on disk (e.g., `- $mnt/data/:/var/lib/milvus`).
    - Add a volume entry below line 47 pointing to the milvus.yml file above (e.g., `/path/to/file/milvus.yaml:/milvus/configs/milvus.yaml`).

Once configured, start Milvus with the following command:

`docker compose up -d`

The containers should download and the service should start running automatically. Further details are available in the Milvus documentation:
- [Install Milvus - Milvus Standalone](https://milvus.io/docs/install_standalone-docker.md)
- [Security - Enable Authorization](https://milvus.io/docs/authenticate.md)

### Setting up Attu (optional)

Milvus can be managed from the command line, but I suggest installing the GUI manager, [Attu](https://github.com/zilliztech/attu). Attu is installed via docker:

`docker run -p 8001:3000 --restart=always -e MILVUS_URL=<Milvus Server IP>:19530 zilliz/attu:v2.3.1`

Once installed, connect to localhost:8001 and login to the root account (default password is Milvus). **Immediately change the password.**

### Create a Collection

This can be done from Attu or programatically. An example of the latter is found in 4-create-collection.ipynb.

### Insert data

Again, this can be done from Attu, but loading anything of substance (i.e., >100MB) should be done programatically, as shown in 5-insert-data.ipynb.

### Create user

Finally, we'll make a new role and user for the Streamlit application, to limit it to read-only access to the Collection we created. This is shown in 6-create-user.ipynb.

## Streamlit

At this point, you should be able to run the application. If you created a user for this application (highly suggested), set the environmental variables in the shell before running the below command or [modify the secrets file in your local streamlit install](https://docs.streamlit.io/library/advanced-features/secrets-management).

`streamlit run --server.port 8081 --server.maxUploadSize 10 --browser.gatherUsageStats false streamlit-milvus.py`

Feel free to change the port or upload limit. `--browser.gatherUsageStats false` simply deactivates telemetry.