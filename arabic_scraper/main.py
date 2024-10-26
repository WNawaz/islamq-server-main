import os

def run_arabic_scraper(finalArabicDataPath: str, spiders_output_directory: str,):
    print("Initialising scraper...")
    print("Arabic Data Path: ", finalArabicDataPath)
    print("English Data Path: ", spiders_output_directory)
    print("Scraper initialised successfully!")


    if not os.path.exists(spiders_output_directory):
        os.makedirs(spiders_output_directory)    

    # Run the spiders
