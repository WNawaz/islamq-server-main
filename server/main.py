from typing import List
from urllib.parse import urlparse
import faiss
import pandas as pd
import numpy as np
import math
import uvicorn
import csv
import simplejson as json
import requests
import math
import nltk

from tempfile import NamedTemporaryFile
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI,Form, Query, HTTPException
import uuid
import shutil

from text_summarisation.main import run_text_summarisation, load_arabart_model, load_bart_model
from translation.main import translate_query_text

english_db_path = ""
arabic_db_path = ""

class ArabicQueryModel(BaseModel):
    query: str
    k: int = 5
    selectedAuthors: List[str] = []
    selectedLinks: List[str] = []

class QueryModel(BaseModel):
    query: str
    k: int = 5
    selectedAuthors: List[str] = []
    selectedLinks: List[str] = []

class ContentTitleAndDescriptionEditQueryModel(BaseModel):
    id: int
    editedTitle: str
    editedContent: str
    language: str

class TitleEditQueryModel(BaseModel):
    id: int
    editedTitle: str
    language: str

class DescriptionEditQueryModel(BaseModel):
    id: int
    editedContent: str
    language: str
    

# Load the text summarisation models only once when the controller script is executed
trained_model = load_arabart_model()
bart_tokenizer, bart_model = load_bart_model()

def get_base_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}/"


def initialize_dataframes_search_model_and_index(
    arabic_db_path_param: str = "data/arabic_data.csv",
    english_db_path_param: str = "data/english_data.csv",
):
    global model, index, df_arabic, df, english_db_path, arabic_db_path

    english_db_path = english_db_path_param
    arabic_db_path = arabic_db_path_param

    df_arabic = pd.read_csv(arabic_db_path)
    df = pd.read_csv(english_db_path)

    # Add missing columns if not present
    if 'link' not in df.columns:
        df['link'] = ''
    if 'author' not in df.columns:
        df['author'] = ''

    if 'link' not in df_arabic.columns:
        df_arabic['link'] = ''
    if 'author' not in df_arabic.columns:
        df_arabic['author'] = ''
    
    # Add isEdited column if not present
    if 'isEdited' not in df.columns:
        df['isEdited'] = False
    if 'isEdited' not in df_arabic.columns:
        df_arabic['isEdited'] = False

    model = SentenceTransformer('all-MiniLM-L6-v2')
    df_arabic = pd.read_csv(arabic_db_path)
    df = pd.read_csv(english_db_path)

    df['title'] = df['title'].fillna('').astype(str)
    df['content'] = df['content'].fillna('').astype(str)
    df['base_link']= df['link'].apply(get_base_url)
    df_arabic['base_link']= df_arabic['link'].apply(get_base_url)

    combined_texts = (df['title'] + ". " + df['content']).tolist()
    embeddings = model.encode(combined_texts, show_progress_bar=True)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype(np.float32))

    

# write a function which only updates the dataframes only
def reload_dataframes(
    arabic_db_path: str = "data/arabic_data.csv",
    english_db_path: str = "data/english_data.csv",
):
    global df_arabic, df
    df_arabic = pd.read_csv(arabic_db_path)
    df = pd.read_csv(english_db_path)
    df['base_link'] = df['link'].apply(get_base_url)
    df_arabic['base_link'] = df_arabic['link'].apply(get_base_url)

def search(query: str, k=5, selected_authors=None, selected_links=None):
    query_embedding = model.encode([query])[0].astype(np.float32)
    distances, indices = index.search(np.array([query_embedding]), k)

    results_df = df.iloc[indices[0]]

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(results_df)

    if selected_authors:
        results_df = results_df[results_df['author'].isin(selected_authors)]
    if selected_links:
        # base_links = [get_base_url(link) for link in selected_links]
        results_df = results_df[results_df['base_link'].isin(selected_links)]
    
    return results_df

    
# create a fastapi instance

app = FastAPI()


def download_nltk_resources():
    # Check if 'punkt' is already downloaded
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        # Download 'punkt' if not available
        nltk.download('punkt')

class SummaryText(BaseModel):
    data: str

@app.post("/summarizeArabic")
def summarize_arabic(text: SummaryText):
    return run_text_summarisation(text.data, "arabic", trained_model, bart_tokenizer, bart_model)

@app.post("/summarizeEnglish")
def summarize_english(text: SummaryText):
    return run_text_summarisation(text.data, "english", trained_model, bart_tokenizer, bart_model)



@app.post("/search-english-data/")
def search_endpoint(query_model: QueryModel):
    try:
        results = search(
            query_model.query, 
            query_model.k, 
            selected_authors=query_model.selectedAuthors, 
            selected_links=query_model.selectedLinks
        )
        # Ensure there are no NaN or infinite values before converting to JSON
        results = results.replace({np.nan: None, np.inf: None, -np.inf: None})
        return {"results": results.to_dict(orient='records')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/search-arabic-data/")
def search_arabic_endpoint(query_model: ArabicQueryModel):
    try:
        # Translate Arabic query to English
        translated_query = translate_query_text(query_model.query, 'en')

        # Use the translated English query to search in the English dataset
        english_results = search(
            translated_query, 
            query_model.k, 
            selected_authors=query_model.selectedAuthors, 
            selected_links=query_model.selectedLinks
        )

        # Map indices from English results to Arabic dataset entries
        arabic_results = df_arabic.iloc[english_results.index]

        # Convert the results to dictionary
        results = arabic_results.to_dict(orient='records')

        # If a result's content is NaN, replace it with the title
        for result in results:
            if pd.isna(result['content']):
                result['content'] = ""
            
            # Replace non-compliant float values
            for key, value in result.items():
                if isinstance(value, float):
                    if math.isinf(value) or math.isnan(value):
                        result[key] = None  # or replace with a default value

        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def update_csv_content(english_index: str, title: str, content: str, file_path: str, isUpdateTitle: bool, isUpdatedDescription: bool):
    try:
        updated_data = []
        print("opening file")

        fieldname = "data/english_data.csv"
        fieldnames = ['index', 'title', 'content', 'link', 'author', 'filter', 'isEdited']
        tempfile = NamedTemporaryFile(mode='w', delete=False)

        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile, tempfile:
            reader = csv.DictReader(csvfile)
            writer = csv.DictWriter(tempfile, fieldnames=fieldnames)           
            print("File Opened")
            print(f"reader: {reader}")

            writer.writerow({'index': 'index', 'title': 'title', 'content': 'content', 'link': 'link', 'author': 'author', 'filter': 'filter', 'isEdited':'isEdited'})

            for row in reader:
                if int(row['index']) == int(english_index):
                    print(f"row found, index: {row['index']}, english_index: {english_index}")
                    # Convert to int for comparison
                    row['isEdited'] = True
                    row['index'] = int(row['index'])
                    row['title'] = row['title']
                    row['author'] = row['author']
                    row['link'] = row['link']
                    row['filter'] = row['filter']
                    if isUpdateTitle:
                        row['title'] = title
                    if isUpdatedDescription:
                        row['content'] = content
                writer.writerow(row)
        print("File updated")
        tempfile.close()

        uid = uuid.uuid4()

        # Create a backup of the original file
        shutil.copy2(file_path, f"{file_path}_{uid}.bak")

        # Move the updated file to the original file path
        shutil.move(tempfile.name, file_path)

        # initialize_model_and_index()

        reload_dataframes()
        return {"message": "Content updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

@app.post("/updateContent")
async def update_content(query_model: ContentTitleAndDescriptionEditQueryModel):
    try:
        print(f"parameter received id value: {query_model.id}, edited Title value: {query_model.editedTitle}, edited Content value: {query_model.editedContent}")
        # Update content in the backend CSV files
        database_filePath = ''
        if query_model.language == 'english':
            database_filePath = english_db_path
        elif query_model.language== 'arabic':
            database_filePath = arabic_db_path
        if query_model.editedTitle and query_model.editedContent:
        # Both title and content are edited
            update_csv_content(english_index=query_model.id, title=query_model.editedTitle, content=query_model.editedContent, file_path=database_filePath, isUpdateTitle=True, isUpdatedDescription=True)
        elif query_model.editedTitle:
            # Only title is edited
            update_csv_content(english_index=query_model.id, title=query_model.editedTitle, content='', file_path=database_filePath, isUpdateTitle=True, isUpdatedDescription=False)
        elif query_model.editedContent:
            # Only content is edited
            update_csv_content(english_index=query_model.id, title='', content=query_model.editedContent, file_path=database_filePath, isUpdateTitle=False, isUpdatedDescription=True)
        return {"message": "Content updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.post("/updateContentTitle")
async def update_content_title(query_model: TitleEditQueryModel):
    try:
        print(f"parameter received id value: {query_model.id}, editedTitle value: {query_model.editedTitle}")
        # Update title in the backend CSV files
        database_filePath = ''
        if query_model.language == 'english':
            database_filePath = english_db_path
        elif query_model.language == 'arabic':
            database_filePath = arabic_db_path 

        update_csv_content(english_index=query_model.id, title=query_model.editedTitle, content='', file_path=database_filePath, isUpdateTitle=True, isUpdatedDescription=False)
        return {"message": "Title updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.post("/updateContentDescription")
async def update_content_description(query_model: DescriptionEditQueryModel):
    try:
        print(f"parameter received id value: {query_model.id}, editedDescription value: {query_model.editedContent}")
        # Update description in the backend CSV files
        database_filePath = ''
        if query_model.language == 'english':
            database_filePath = english_db_path
        elif query_model.language == 'arabic':
            database_filePath = arabic_db_path  
        update_csv_content(english_index=query_model.id, title='', content=query_model.editedContent, file_path=database_filePath, isUpdateTitle=False, isUpdatedDescription=True)
        return {"message": "Description updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")



# create an endpoint which returns all the data in the arabic dataset in a paginated manner
@app.get("/getArabicData")
async def get_arabic_data(page: int = Query(1, ge=1)):
    try:

        start = (page - 1) * 20
        end = 5292
        paginated_data = df_arabic.iloc[start:end].to_dict(orient='records')
        return json.dumps({"results": paginated_data}, ignore_nan=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    

# create an endpoint which returns all the data in the english dataset in a paginated manner
@app.get("/getEnglishData")
async def get_arabic_data(page: int = Query(1, ge=1)):
    try:
        start = (page - 1) * 20
        end = 5350
        paginated_data = df.iloc[start:end].to_dict(orient='records')
        return json.dumps({"results": paginated_data}, ignore_nan=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
# @app.get("/summarise-arabic")
# async def summarize_arabic_data(content: str = Query(...)):
#     try:
#         # Summarize the Arabic data

#         # send a request to the summarization API
#         # get the response
#         # return the response

        
#         response = requests.post("http://localhost:8000/summarize-arabic", json={"text": content})
#         return {
#             "summary": response.json()['summary']
#         }
#         pass
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# @app.get("/summarise-english")
# async def summarize_english_data(content: str = Query(...)):
#     try:
#         response = requests.post("http://localhost:8000/summarize-english", json={"text": content})
        
#         # Check if the request was successful
#         if response.status_code != 200:
#             raise HTTPException(status_code=500, detail=f"Internal Server Error: API request failed with status {response.status_code}")
        
#         print(f"Response: {response.json()}")
#         # Check if the response contains valid JSON
#         json_response = response.json()
#         if json_response is None:
#             raise HTTPException(status_code=500, detail=f"Internal Server Error: API response does not contain valid JSON")
        
#         # Check if the JSON contains a 'summary' key
#         if 'summary' not in json_response:
#             raise HTTPException(status_code=500, detail=f"Internal Server Error: API response does not contain a 'summary' key")
        
#         return {
#             "summary": json_response['summary']
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    

@app.get("/getExploreArabicContent")
async def get_explore_arabic_content():
    try:
        # Get the first 5 rows from the Arabic dataset
        explore_data = df_arabic[df_arabic['content'].notna() & df_arabic['content'] != ''].iloc[:10].to_dict(orient='records')
        return json.dumps({"results": explore_data}, ignore_nan=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
    
@app.get("/getExploreEnglishContent")
async def get_explore_english_content():
    try:
        # Get the first 5 rows from the English dataset, whose content is not NaN or empty
        explore_data = df[df['content'].notna() & df['content'] != ''].iloc[:10].to_dict(orient='records')

        # convert explore_data to dict
        return json.dumps({"results": explore_data}, ignore_nan=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
    
@app.delete("/deleteContent/{id}")
async def delete_content(id: int):
    try:
        print(f"Deleting content with ID: {id}")
        
        # if language == 'english':
        df_english = pd.read_csv(english_db_path)
        database_filePath_english = english_db_path
        # elif language == 'arabic':
        df_arabic = pd.read_csv(arabic_db_path)
        database_filePath_arabic = arabic_db_path
        # else:
        #     raise HTTPException(status_code=400, detail="Invalid language specified")

        if id not in df['index'].values:
            raise HTTPException(status_code=404, detail=f"Content with ID {id} not found")

        df_english = df_english[df_english['index'] != id]
        df_english.to_csv(database_filePath_english, index=False)

        df_arabic = df_arabic[df_arabic['index'] != id]
        df_arabic.to_csv(database_filePath_arabic, index=False)

        reload_dataframes()

        return {"message": f"Content with ID {id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
    

@app.get("/englishAuthorsAndLinks")
async def english_authors_and_links(isAdminsOrVolunteers: bool):
    try:
        if not isAdminsOrVolunteers:
            df_filtered = df[df['isEdited'] == True]
        else:
            df_filtered = df
        unique_links = df_filtered['link'].dropna().unique().tolist()
        unique_authors = df_filtered['author'].dropna().unique().tolist()
        base_links = [get_base_url(link) for link in unique_links]
        return {"authors": unique_authors, "links": set(list(base_links))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    

@app.get("/arabicAuthorsAndLinks")
async def arabic_authors_and_links(isAdminsOrVolunteers: bool):
    try:
        if not isAdminsOrVolunteers:
            df_filtered = df_arabic[df_arabic['isEdited'] == True]
        else:
            df_filtered = df_arabic
        unique_links = df_filtered['link'].dropna().unique().tolist()
        unique_authors = df_filtered['author'].dropna().unique().tolist()
        base_links = [get_base_url(link) for link in unique_links]
        return {"authors": unique_authors, "links": base_links}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    
@app.post("/search-edited-english-data/")
def search_edited_english_endpoint(query_model: QueryModel):
    try:
        # Load the dataset
        df_english = pd.read_csv(english_db_path)
        
        # Perform search to get the initial results
        search_results = search(
            query_model.query, 
            query_model.k, 
            selected_authors=query_model.selectedAuthors, 
            selected_links=query_model.selectedLinks
        )
        
        # Get indices of the search results
        result_indices = search_results.index
        
        # Filter the dataset for the edited rows
        edited_rows = df_english.loc[result_indices]
        edited_rows = edited_rows[edited_rows['isEdited'] == True]
        
        # Convert to dictionary format for response
        results = edited_rows.to_dict(orient='records')

        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")




@app.post("/search-edited-arabic-data/")
def search_edited_arabic_endpoint(query_model: ArabicQueryModel):
    try:
        # Load the dataset
        df_arabic = pd.read_csv(arabic_db_path)
        
        # Translate the query to English
        translated_query = translate_query_text(query_model.query, 'en')
        
        # Perform search on English dataset
        search_results = search(
            translated_query, 
            query_model.k, 
            selected_authors=query_model.selectedAuthors, 
            selected_links=query_model.selectedLinks
        )
        
        # Get indices of the search results
        result_indices = search_results.index
        
        # Filter the dataset for the edited rows
        edited_rows = df_arabic.loc[result_indices]
        edited_rows = edited_rows[edited_rows['isEdited'] == True]
        
        # Convert to dictionary format for response
        results = edited_rows.to_dict(orient='records')

        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
    
    


@app.get("/getEditedExploreEnglishContent")
async def get_edited_explore_english_content():
    try:
        # Get rows from the English dataset where isEdited is True
        edited_explore_data = df[(df['isEdited'] == True) & (df['content'].notna()) & (df['content'] != '')].iloc[:10].to_dict(orient='records')


        # Log the type and value of 'index'
        for result in edited_explore_data:
            print(f"Index type: {type(result['index'])}, Index value: {result['index']}")

        return json.dumps({"results": edited_explore_data}, ignore_nan=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    

    
@app.get("/getEditedExploreArabicContent")
async def get_edited_explore_arabic_content():
    try:
        # Get rows from the Arabic dataset where isEdited is True
        edited_explore_data = df_arabic[(df_arabic['isEdited'] == True) & (df_arabic['content'].notna()) & (df_arabic['content'] != '')].iloc[:10].to_dict(orient='records')
        return json.dumps({"results": edited_explore_data}, ignore_nan=True)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


def run_server(
    host: str = "0.0.0.0",
    port: int = 4000,
    debug: bool = False,
    arabicDataPath: str = "data/arabic_data.csv",
    englishDataPath: str = "data/english_data.csv",
):

    print("Initialising server...")
    print("Host: ", host)
    print("Port: ", port)
    print("Debug: ", debug)
    print("Arabic Data Path: ", arabicDataPath)
    print("English Data Path: ", englishDataPath)
    
    initialize_dataframes_search_model_and_index(arabicDataPath, englishDataPath)
    download_nltk_resources()

    # Run the server
    uvicorn.run(app, host=host, port=port)

    print("Server initialised successfully!")

