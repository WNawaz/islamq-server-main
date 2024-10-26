import csv
import asyncio
import aiohttp  # Might still be needed for future external API calls
import time
import os
import argparse

from langdetect import detect, DetectorFactory
from googletrans import Translator


# Avoid repeated overhead in detecting languages
DetectorFactory.seed = 0

translator = Translator()


async def translate_text(text, source_lang, target_lang):

    max_chunk_size = 5000  # max chunk size to be sent in one request

    print(f"Translating text: {text}")
    """
    Translates text with chunking if necessary.
    """
    if len(text) <= max_chunk_size:
        try:
            translated_text = translator.translate(
                text, src=source_lang, dest=target_lang).text
            return translated_text
        except Exception as e:
            print(f"Error translating text: {text}. Exception: {e}")
            return text
    else:
        # Chunk and translate
        chunks = [text[i:i + max_chunk_size]
                  for i in range(0, len(text), max_chunk_size)]
        translated_chunks = []
        for chunk in chunks:
            translated_chunk = await translate_text(chunk, source_lang, target_lang)
            translated_chunks.append(translated_chunk)
        return ''.join(translated_chunks)


async def translate_batch(batch):
    start_time = time.time()  # Record start time
    translations = []

    for text in batch:
        try:
            lang = detect(text)
            target_lang = "en" if lang == "ar" else "ar"
            translated_text = await translate_text(text, lang, target_lang)
            translations.append(translated_text)

        except Exception as e:
            print(f"Error translating text: {text}. Exception: {e}")
            translations.append(text)

    end_time = time.time()  # Record end time
    batch_duration = end_time - start_time

    log_message = f"Script execution completed. Duration: {batch_duration:.2f} seconds.\n"
    with open("translation_log.txt", "a") as log_file:
        log_file.write(log_message)
        print(log_message)

    return translations


async def process_batch(batch):
    print(f"Processing batch of {len(batch)} rows")
    # Unpack the batch while ignoring the index
    _, titles, contents,_,_ = zip(*batch)  # Add a placeholder for the index
    print("Translating titles...")
    translated_titles = await translate_batch(titles)
    print("Translating contents...")
    translated_contents = await translate_batch(contents)

    # Keep the original index from the batch for each row
    translated_rows = list(
        zip([index for index, _, _, _, _ in batch], translated_titles, translated_contents))
    return translated_rows


async def initiateScrapedDataTranslation(
        CSV_FILE,
        TRANSLATED_CSV_FILE,
        BATCH_SIZE=10
):

    if not os.path.exists(CSV_FILE):
        print(f"File {CSV_FILE} does not exist.")
        return

    file_exists = os.path.exists(TRANSLATED_CSV_FILE)

    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as csvfile, \
            open(TRANSLATED_CSV_FILE, 'a', newline='', encoding='utf-8') as translated_csv:
        reader = csv.DictReader(csvfile)
        print("Loaded Reader...")
        writer = csv.DictWriter(translated_csv, fieldnames=[
                                "index", "title", "content", "link", "author",])
        print("Loaded Writer...")

        writer.writeheader()

        batch = []
        async with aiohttp.ClientSession() as session:
            for row in reader:
                batch.append((row['index'], row['title'],
                             row['content'], row['link'], row['author']))
                if len(batch) == BATCH_SIZE:
                    translated_rows = await process_batch(batch)
                    for idx, title, content in translated_rows:
                        writer.writerow(
                            {'index': idx, 'title': title, 'content': content,
                             'link': row['link'], 'author': row['author'], })
                    batch = []  # Clear batch after processing

            # Process any remaining items in the batch
            if batch:
                translated_rows = await process_batch(batch)
                for idx, title, content in translated_rows:
                    writer.writerow(
                        {'index': idx, 'title': title, 'content': content})


if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser(description='Translate scraped data')
    parser.add_argument('--input', type=str, help='Input CSV file')
    parser.add_argument('--output', type=str, help='Output CSV file')
    parser.add_argument('--batch_size', type=int,
                        default=10, help='Batch size')
    args = parser.parse_args()

    if args.input:
        CSV_FILE = args.input
    if args.output:
        TRANSLATED_CSV_FILE = args.output
    if args.batch_size:
        BATCH_SIZE = args.batch_size

    asyncio.run(initiateScrapedDataTranslation(
        CSV_FILE, TRANSLATED_CSV_FILE, BATCH_SIZE,
    ),)
