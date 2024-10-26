import asyncio
import time
import pandas as pd
import csv
import os

from googletrans import Translator

translator = Translator()


def translate_query_text(text: str, target_language: str) -> str:
    """Translate a search query text to the specified destination language."""
    try:
        return translator.translate(text, dest=target_language).text
    except Exception as e:
        print(f"An error occurred: {e}")
    

async def translate_chunk(chunk: str, dest_language: str = 'en') -> str:
    """Translate a chunk of text to the specified destination language."""
    try:
        return translator.translate(chunk, dest=dest_language).text
    except Exception as e:
        print(f"An error occurred: {e}")
        
async def translate_text(text: str, dest_language: str = 'en') -> str:
    """Translate text to the specified destination language."""
    print("Translating Text")
    try:
        if len(text) > 5000:
            print("Text is too long. Splitting into chunks...")
            chunks = [text[i:i+5000] for i in range(0, len(text), 5000)]
            coros = [translate_chunk(chunk=chunk) for chunk in chunks]
            translated_chunks = await asyncio.gather(*coros)
            translated_text = ''.join([chunk for chunk in translated_chunks])
        else:
            translated_text = translator.translate(text, dest=dest_language).text
        return translated_text
    except Exception as e:
        print(f"An error occurred: {e}")


async def translate_texts(texts: list, dest_language: str = 'en') -> list:
    """Translate a list of texts to the specified destination language."""
    tasks = [translate_text(text, dest_language) for text in texts]
    translated_texts = await asyncio.gather(*tasks)
    return translated_texts

async def translate_csv(input_file: str, output_file: str, dest_language: str = 'en'):
    print("Translating csv")
    
    # Check if the output file exists
    if os.path.exists(output_file):
        print("The output file already exists")
        # Read the output CSV file to get already translated links
        translated_links = set(pd.read_csv(output_file)['link'])
        
        # Read the input CSV file
        input_df = pd.read_csv(input_file)
        
        # Filter out rows that are not already translated
        rows_to_translate = input_df[~input_df['link'].isin(translated_links)]
    else:
        print("The output file does not exist")
        # If output file doesn't exist, translate all rows from input file
        rows_to_translate = pd.read_csv(input_file)

    print(f"Rows to translate: {len(rows_to_translate)}")

    # Create batches of rows for translation
    batch_size = 10
    num_batches = (len(rows_to_translate) + batch_size - 1) // batch_size

    for i in range(num_batches):
        start_index = i * batch_size
        end_index = min((i + 1) * batch_size, len(rows_to_translate))
        batch = rows_to_translate.iloc[start_index:end_index]

        # Translate the titles and contents
        batch['title'] = await translate_texts(batch['title'].tolist(), dest_language)
        batch['content'] = await translate_texts(batch['content'].tolist(), dest_language)

        # Append translated rows to the output CSV file
        batch.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False)

        print(f"Translated and written batch {i + 1}/{num_batches}")

    print("Translation complete.")


# start_time = time.time()

# # Example usage
# texts = ['Hello', 'How are you?', 'Goodbye',
#          'Hello', 'How are you?', 'Goodbye',
#          'Hello', 'How are you?', 'Goodbye',
#          'Hello', 'How are you?', 'Goodbye',
#          'Hello', 'How are you?', 'Goodbye',
#          'Hello', 'How are you?', 'Goodbye',
#          'Hello', 'How are you?', 'Goodbye',
#          'Hello', 'How are you?', 'Goodbye','Hello', 'How are you?', 'Goodbye','Hello', 'How are you?', 'Goodbye','Hello', 'How are you?', 'Goodbye','Hello', 'How are you?', 'Goodbye','Hello', 'How are you?', 'Goodbye',
         
         
         
         
#          ]

# translated_texts = asyncio.run(translate_texts(texts, 'fr'))
# end_time = time.time()

# print(f"Time taken: {end_time - start_time} seconds")

# print(translated_texts)
