import os
import glob
import subprocess
import pandas as pd
import asyncio
import uvicorn
import threading
import time

# from apscheduler.schedulers.asyncio import AsyncIOScheduler

from arabic_scraper.run_arabic_spiders import run_crawl_and_reactor
from translation.main import translate_csv
from server.main import run_server,reload_dataframes
from speech_recognition.main import run_speech_recognition

# scraper configurations

enlish_data_uri = 'data/english_data.csv'
feed_uri = 'data/arabic_data.csv'

feed_format = 'csv'
feed_spiders_dir = 'data/spiders'
feed_export_encoding = 'utf-8'
csv_export_headers = False

def validate_data_exists():
    # Check if English data file and Arabic data file exist
    english_data_exists = os.path.exists('data/english_data.csv')
    arabic_data_exists = os.path.exists('data/arabic_data.csv')

    # Return True if both files exist, otherwise return False
    return english_data_exists and arabic_data_exists

def combine_csv_files():
    print("Combining CSV files")
    # Get a list of all CSV files in the feed_spiders_dir folder
    csv_files = glob.glob(os.path.join(feed_spiders_dir, '*.csv'))

    # Combine all CSV files into one DataFrame
    combined_data = pd.concat([pd.read_csv(file) for file in csv_files])

    # Load existing data if it exists
    if os.path.exists(feed_uri):
        existing_data = pd.read_csv(feed_uri)
        
        # Extract unique links from the existing data
        existing_links = set(existing_data['link'])
        # Print the length of the existing links list
        print("Length of existing links list:", len(existing_links))

        # Filter out rows with links already present in the existing data
        new_data = combined_data[~combined_data['link'].isin(existing_links)].dropna()

        # Define the specific headers row
        specific_headers_row = ['content', 'title', 'author', 'link', 'filter']

        # Check if the new data contains the specific headers row
        is_specific_headers_row = new_data.apply(lambda row: row.tolist() == specific_headers_row, axis=1)

        # Filter out the rows containing the specific headers row
        new_data_filtered = new_data[~is_specific_headers_row]

        print("Length of new data (new links):", len(new_data_filtered))

        # Append new data to existing data (if any)
        combined_data = pd.concat([existing_data, new_data_filtered], ignore_index=True)
    else:
        print("No previous data exists hence treat all data as new data")


    # Drop the index column
    combined_data.drop(columns=['Unnamed: 0'], inplace=True, errors='ignore')

    # Assign integer values to the index column
    combined_data['index'] = range(1, len(combined_data) + 1)

    print("Saving combined data to a new CSV file")
    # Save the combined data to the existing CSV file
    combined_data.to_csv(feed_uri, encoding='utf-8', index=False)
    print("Data saved to", feed_uri)

    print("Removing curernt spider files")
    # Remove all files in feed_spiders_dir
    for file_path in glob.glob(os.path.join(feed_spiders_dir, '*')):
        os.remove(file_path)
        print("Removed file:", file_path)


def run_arabic_audio_scraper_with_speech_recognition_and_translation():

    try:
        # scraper_arabic_data_output_file_path = config['DATA']['data_arabic_csv_path']
        # scraper_arabic_data_output_dir_path = config['SCRAPER']['arabic_audio_feed_dir']

        # translator_english_data_output_dir = config['DATA']['data_english_csv_path']

        scraper_arabic_data_output_file_path = "./data/arabic/combined_audio_urls.csv"
        scraper_arabic_data_output_dir_path = "./data/arabic/audio"
        translator_english_data_output_file = "./data/translated_text.csv"

        speech_recognised_data_output_file_path = "./data/arabic/audio/alharamain_audios_transcribed.csv"

        #call the following program which receives the following argument: --output
        subprocess.call(["python3", "./audio_scrapper/ar_audio_scraper/run-audio-scraper.py",
                        "--output", scraper_arabic_data_output_file_path, "--output_dir", scraper_arabic_data_output_dir_path])
        print("Audio scraping completed. Sending audio to Whisper...")


        # call the speech recognition programm, argument: --input_file, --output. --output_dir, --localhost_ip
        subprocess.call(["python3", "speech_recognition/speech_recognition_api.py",
                        "--input_file", scraper_arabic_data_output_file_path, "--output", speech_recognised_data_output_file_path, "--output_dir", scraper_arabic_data_output_dir_path, "--localhost_ip", "http://localhost:9000/asr"])
        print("Whisper processing completed.")


        # input arabic data and output english data
        run_translator(speech_recognised_data_output_file_path,
                       translator_english_data_output_file)

    except Exception as e:
        print("Error in run_arabic_scraper_with_translation: ", e)


def run_translator(input_dir, output_dir):

    try:

        subprocess.call(
            ["python", "translator/translator_batch.py", "--input", input_dir, "--output", output_dir])

    except Exception as e:
        print("Error in run_translator: ", e)


def process_scrape_data():
    combine_csv_files()
    loop = asyncio.new_event_loop()  # Create a new event loop
    asyncio.set_event_loop(loop)     # Set it as the current event loop
    try:
        loop.run_until_complete(translate_csv(feed_uri, enlish_data_uri, 'en'))
    finally:
        loop.close()  # Close the event loop
    reload_dataframes()

def arabic_text_pipeline():
    run_crawl_and_reactor()
def run_controller():
    if not validate_data_exists():
        arabic_text_pipeline()

    # Start the server
    thread_server = threading.Thread(target=run_server)
    thread_server.start()
    thread_server.join()

    # Run the text scraper
    arabic_text_pipeline()

    # Process the scraped data
    process_scrape_data()

    # Run the audio scraper and send audio files to Whisper
    run_arabic_audio_scraper_with_speech_recognition_and_translation()

if __name__ == "__main__":
    run_controller()