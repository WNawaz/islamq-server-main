# Islamq Backend Server

Forwaded Server IP: https://fe5e-119-156-232-132.ngrok-free.app

## Project Summary

**Islamq** is a project designed to help users quickly navigate through the opinions of multiple Islamic scholars. This is achieved by providing a search engine where users can enter a topic and receive opinions from various Islamic scholars.

## Technical Details

### Scraper

The backend features a web scraper that scrapes textual data from multiple Arabic scholar websites. The scraped data is formatted into the following columns:

1. **Title**: The heading of the topic.
2. **Content**: All content related to the topic from the webpage.
3. **Author**: The scholar whose content is being scraped (hardcoded in each spider's config).
4. **Link**: The link of the webpage from where the data was scraped.
5. **Filter**: The topic's category as mentioned on the website being scraped (hardcoded in the spider’s config).

#### Spider Details

- Multiple individual spiders are crafted for specific websites/webpages.
- Custom spiders reduce the overhead compared to a general spider due to varied webpage formats.
- Spiders are controlled by a `CrawlerRunner`, which runs all spiders in parallel (found in `arabic_scraper/run-all-spider.py`).
- The scraper job is scheduled to run every 7 days.

#### Data Handling

- Scraped data is stored in `data/spiders` in `.csv` format, named after the spider.
- The data from all spiders is combined into `data/arabic_data.csv` with headers: `Content`, `Title`, `Author`, `Link`, `Filter`, `Index`.
- `process_scrape_data` function handles data consolidation and ensures only new data is added to the final output file.
- The new data is then translated to the target language.

### Search

The search mechanism employs the FAISS library with an L2 distance search. 

#### Search Algorithm

1. **Data Loading and Preparation**:
    - CSV files with English and Arabic datasets are loaded into Pandas DataFrames.
    - Missing values in titles and content are filled with empty strings.
2. **Text Embedding**:
    - `SentenceTransformer` model (`all-MiniLM-L6-v2`) converts text into numerical embeddings.
3. **Index Creation**:
    - Embeddings are combined and fed into a FAISS index (`IndexFlatL2`) for efficient nearest-neighbor search.

#### Search Functionality

- **Initialization**:
    - `initialize_dataframes_search_model_and_index`: Reads datasets, initializes the model, combines text fields, generates embeddings, and creates the FAISS index.
- **Execution**:
    - `search`: Takes a query string and optional parameter `k`, encodes the query, searches the FAISS index, and returns the nearest neighbors.

#### API Endpoints

- **English Data Search**:
    - **Endpoint**: `/search-english-data/`
    - **Input**: Query and `k` via POST request.
    - **Output**: Search results in JSON format.
- **Arabic Data Search**:
    - **Endpoint**: `/search-arabic-data/`
    - **Input**: Query and `k` via POST request.
    - **Process**: Translates Arabic query to English, searches the English dataset, maps results back to Arabic dataset, handles missing values, and returns results in JSON format.

### Translation

The translation module uses the Google Translate API to translate content from a source language to the target language.

1. **Initialization**:
    - Imports libraries: asyncio, time, pandas, csv, os.
    - Creates a Translator object from `googletrans` library.
2. **Translation Functions**:
    - **Synchronous**:
        - `translate_query_text`: Translates a single search query.
    - **Asynchronous**:
        - `translate_chunk`: Translates a chunk of text asynchronously.
        - `translate_text`: Handles asynchronous text translation.
        - `translate_texts`: Translates a list of texts asynchronously.
3. **CSV Translation**:
    - `translate_csv`: Translates CSV file contents asynchronously, handling batch processing and avoiding duplication. Reads input CSV, translates necessary rows, and writes to an output CSV.

### Text Summarization

The text summarization module uses abstraction methods and supports English and Arabic.

- **Models Used**:
    - English: `facebook/bart-large-cnn`
    - Arabic: `AraBart`
- **Functionality**:
    - Receives text and language as parameters, processes them, and returns the textual summary.

### Audio Scraper and Whisper

#### Audio Scraper:
Audio scraper to collect Arabic audio URLs:
- The audio scraper collects Arabic audio URLs and saves them in ./data/arabic/combined_audio_urls.csv 
- Audio files are saved in ./data/arabic/audio

#### Whisper:
- After the audio has been scraped, whispher will use these to transcribe the audio files. 
- Make sure the Whisper server running on a separate port. For instance, run Whisper on port 9000 using Docker.
- The transcribed files are saved in ./data/translated_text.csv.

# How to run
## Step 1: Whisper
### Prerequisites
1. **Install Docker**: Ensure that Docker is installed on your system. You can download it from [Docker's official site](https://www.docker.com/get-started).
2. **Docker Daemon**: Verify that the Docker daemon is running. You can start it using the following command:
   ```bash
   sudo systemctl start docker
   ```

### Steps

#### Step 1: Pull the Whisper Docker Image
Before running a container, you need to pull the Whisper image from a Docker registry (e.g., Docker Hub). Use the following command to pull the image:
```bash
docker pull onerahmet/openai-whisper-asr-webservice
```
This will download the Whisper image to your local Docker repository.

#### Step 2: Verify the Whisper Docker Image
Once the image has been pulled, confirm it exists on your system by listing all Docker images:
```bash
docker images
```
You should see `onerahmet/openai-whisper-asr-webservice` in the output.

#### Step 3: Run the Whisper Docker Container
Now, run the Whisper Docker container on a specified port (e.g., port 9000). Use the following command:
```bash
docker run -d -p 9000:9000 onerahmet/openai-whisper-asr-webservice
```
Explanation:
- **`-d`**: Runs the container in detached mode, so it runs in the background.
- **`-p 9000:9000`**: Maps port 9000 of the host to port 9000 of the container. Modify the port number as needed.

#### Step 4: Verify the Container is Running
You can check whether the container is running using the following command:
```bash
docker ps
```
This command lists all running containers. Look for `onerahmet/openai-whisper-asr-webservice` in the output to confirm that your Whisper container is active.

#### Step 5: Access the Whisper Service
Once the container is running, you should be able to access the Whisper service via the mapped port on your host machine. For example, if you mapped to port 9000, access the service at `http://localhost:9000`.

## Step 2: Server Docker Container
Now, run the server Docker container.
### Prerequisites
#### Clone this repo
- Clone this repo
- Install its packages from requirements.txt

### Steps
### 1. Build the Server Docker Image
1. Build the docker image using `docker build -t islamq-server`

### 2. Run the Server Docker Image
Run the docker container using `docker run -p 4000:4000 islamq-server`

You will be able to see the docker running on localhost:4000
You can also see the API docs at localhost:4000/docs

### Step 3: Run the Python Controller
After ensuring both Docker containers (Whisper and Server) are up and running, you need to run the Python controller to scrape data, process it, and manage the entire pipeline. Follow the steps below to execute the script:

## Run the Python Controller Script:
Execute the following command in your terminal:`python3 controller.py` 

### This script performs the following actions:
- Validation: It checks if the necessary data files exist (english_data.csv and arabic_data.csv).
- Server Start: It starts the server in a separate thread, allowing the application to handle incoming requests.
- Arabic Text Scraping: It runs a web crawler to scrape Arabic text data, storing the results in CSV files.
- Data Processing: It combines the scraped data with existing data, removes duplicates, and ensures the final dataset is up-to-date.

Here are step-by-step instructions for installing and using ngrok to expose your local server to the internet, and how to use the ngrok URL in your app to access the server.

## Step 3. Use ngrok
The purpose of using ngrok is to make your local server accessible to anyone on the internet. It creates a secure, public URL that forwards traffic to your local server, allowing your client-side app to connect to your server from anywhere in the world using this ngrok-generated URL.

### Step 1: Install ngrok

1. **Download ngrok**  
   Go to the [ngrok website](https://ngrok.com/download) and download the version for your operating system (Windows, macOS, or Linux).

2. **Install ngrok**
   - **Windows**: Extract the downloaded ZIP file, and move the `ngrok.exe` file to a directory of your choice. Optionally, add this directory to your PATH for easy access.
   - **macOS/Linux**: Extract the downloaded file and move it to `/usr/local/bin` for global access:
     ```bash
     sudo mv ngrok /usr/local/bin
     ```

3. **Sign Up and Authenticate**
   - Create an account on ngrok (if you don’t have one).
   - Once logged in, you'll find your **Auth Token** under the "Get Started" section. Copy it.
   - Run the following command to authenticate your ngrok installation:
     ```bash
     ngrok config add-authtoken <YOUR_AUTH_TOKEN>
     ```

### Step 2: Run Your Local Server

Before exposing your local server, ensure that it is running. For example, if you're running a Docker container on port `9000`, ensure that the server is accessible on your local IP (e.g., `http://localhost:9000`).

### Step 3: Expose Your Local Server with ngrok

To expose your local server, use the following command:
```bash
ngrok http <local_port>
```
Replace `<local_port>` with the port number your server is running on (e.g., `9000` if you’re using Docker). For example:
```bash
ngrok http 9000
```

### Step 4: Get the ngrok URL

After running the above command, ngrok will display a public URL (e.g., `http://<subdomain>.ngrok.io`). This URL can be used to access your local server from the internet.

Here’s an example output:
```
Session Status                online
Account                       YourAccount (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Web Interface                 http://127.0.0.1:4040
Forwarding                    http://abcd1234.ngrok.io -> http://localhost:9000
Forwarding                    https://abcd1234.ngrok.io -> http://localhost:9000
```

The URL `http://abcd1234.ngrok.io` (or the HTTPS version) is your public URL.

### Step 5: Use the ngrok URL in Your App

Now that you have the ngrok URL, you can use it in your application to access your local server from anywhere. For example, if your app connects to the server at `http://localhost:9000`, replace `localhost:9000` with the ngrok URL (`http://abcd1234.ngrok.io`).

If you're making API requests in your app, ensure that you update all endpoints to use the ngrok URL.

# System Requirements

## Hardware Requirements
- **CPU**: AMD Ryzen 5 3600 or Intel equivalent (6 cores, 12 threads)
- **RAM**: 16 GB DDR4 or higher
- **GPU**: NVIDIA GTX 1070 (8 GB VRAM) or equivalent for GPU-accelerated tasks. Ensure that the GPU supports CUDA if using GPU for inference.

### Additional Considerations:
- **Storage**: SSD with at least 20 GB of free space for Docker images and temporary data storage.
- **Network**: Reliable network connection for pulling Docker images and potentially for serving APIs.

## Software Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS, or Windows 10/11 with WSL 2 for Linux-based Docker containers.
- **Docker**: Docker Engine (version 20.10+)
  - Ensure the Docker daemon is running and that you have sufficient permissions to execute Docker commands.
- **Python**: Python 3.7+ (only required if additional Python-based setup scripts or tools are needed outside of Docker)
- **NVIDIA Docker (optional)**: Required for GPU acceleration with Docker. Install NVIDIA Docker Toolkit to enable GPU support within Docker containers:
  ```bash
  sudo apt-get install -y nvidia-docker2
  ```
