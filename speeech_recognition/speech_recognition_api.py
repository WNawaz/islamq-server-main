import argparse
import csv
import time
import requests
import argparse
import csv
import requests
import subprocess
from pydub import AudioSegment

def send_audio_files(csv_file_path, localhost_ip, output_file_path):
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        with open(output_file_path, 'w') as output_file:
            writer = csv.writer(output_file)
            for row in reader:
                audio_link = row.get('audio_links')
                # each row contains multiple links separated by commas
                audio_links = audio_link.split(',')
                
                for audio_link in audio_links:
                    if audio_link:
                        # track start time of this link processing

                        start_time = time.time()

                        print(f"Downloading audio file from {audio_link}")
                        response = requests.get(audio_link)
                        if response.status_code == 200:
                            print(f"Downloaded audio file from {audio_link}")
                            audio_file = response.content
                            # write the audio file to local storage, use the same filename as the audio link
                            with open(f"{output_dir}/{audio_link.split('/')[-1]}", 'wb') as f:
                                f.write(audio_file)

                            files = {'audio_file': audio_file}
                            # duration = get_audio_duration(f"{output_dir}/{audio_link.split('/')[-1]}" )
                            # if duration > 20 * 60:  # Check if duration is greater than 20 minutes
                            #     print(f"Skipping audio file from {audio_link} due to long duration")
                            #     writer.writerow([audio_link, "Audio duration greater then 20 mins, Skipped."])
                            #     continue

                            response = requests.post(localhost_ip, files=files)
                            print('Response:', response.text)
                            print(f"Sent audio file to localhost {localhost_ip}")
                            writer.writerow([audio_link, response.text])
                            end_time = time.time()
                        else:
                            print(f"Failed to download audio file from {audio_link}")
                            writer.writerow([audio_link, response.status_code])
                            end_time = time.time()
                            
                        print(f"Time taken to process {audio_link}: {end_time - start_time} seconds")

def get_audio_duration(audio_file):
    audio = AudioSegment.from_file(audio_file)
    duration = len(audio) / 1000  # duration in seconds
    return duration

if __name__ == '__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser(description='Run audio scraper')
    parser.add_argument('--input_file', type=str, default='islamic_dataset.csv', help='Input filename')
    parser.add_argument('--output', type=str, default='islamic_dataset.csv', help='Output filename')
    parser.add_argument('--output_dir', type=str, default='data/arabic', help='Output directory')
    parser.add_argument('--localhost_ip', type=str, default='http://localhost:8080', help='Localhost IP address')
    args = parser.parse_args()
    # if args argument is not provided, exit
    if not args:
        print("No arguments provided. Exiting...")
        exit()
    if args.input_file:
        input_file = args.input_file
    if args.output:
        output_filename = args.output
    if args.output_dir:
        output_dir = args.output_dir
    if args.localhost_ip:
        localhost_ip = args.localhost_ip
    print(f"Input filename: {input_file}")
    print(f"Output filename: {output_filename}")
    print(f"Output directory: {output_dir}")
    print(f"Localhost IP address: {localhost_ip}")
    send_audio_files(input_file, localhost_ip, output_filename)

