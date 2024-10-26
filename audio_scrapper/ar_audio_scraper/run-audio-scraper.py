import glob
import csv
import time
import argparse

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from ar_audio_scraper.spiders.alharmainaudio import AlharamainAudioSpider

# Import other spiders here

def run_spiders():
    # Initialize a Scrapy crawler process with your project's settings
    process = CrawlerProcess(get_project_settings())
    
    # Add your spiders
    process.crawl(AlharamainAudioSpider)

    # Start the crawling process
    process.start()
    time.sleep(1)

def combine_csv(output_filename='islamic_dataset.csv', output_dir='data/audio/arabic'):
    # Adjust fieldnames to include 'index'
    fieldnames = ['index', 'title', 'audio_links']
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Initialize index counter
        index = 1
        # Iterate over all CSV files in the ouput directory "data/"
        for filename in glob.glob(f'{output_dir}/*.csv'):
            if filename == output_filename:  # Skip the combined output file
                continue
            print(f"Combining {filename}...")
            with open(filename, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    print(row)
                    # Add the current index to the row before writing
                    row['index'] = index
                    writer.writerow(row)
                    index += 1  # Increment the index for the next row
    
    time.sleep(2)

def log_execution_time(func_name, start_time, end_time):
    """Logs the execution time of a function to a text file."""
    with open('execution_log.txt', 'a') as file:  # Changed to .txt extension
        # Simplified logging format for text
        log_message = f"{func_name}, {start_time}, {end_time}, {end_time - start_time}\n"
        file.write(log_message)



if __name__ == '__main__':

    # parse command line arguments

    parser = argparse.ArgumentParser(description='Run audio spiders and combine CSV files')
    parser.add_argument('--output', type=str, default='islamic_audio_dataset.csv', help='Output filename')
    parser.add_argument('--output_dir', type=str, default='data/arabic', help='Output directory')
    args = parser.parse_args()

    # if args argument is not provided, exit
    if not args:
        print("No arguments provided. Exiting...")
        exit()

    if args.output:
        output_filename = args.output

    print(f"Output filename: {output_filename}")

    # Measure and log execution time for run_spiders
    start_time = time.time()
    run_spiders()
    end_time = time.time()
    log_execution_time('audio_run_spiders', start_time, end_time)

    # Measure and log execution time for combine_csv
    start_time = time.time()
    combine_csv(
        output_filename=output_filename,
        output_dir=args.output_dir
    )
    end_time = time.time()
    log_execution_time('audio_combine_csv', start_time, end_time)