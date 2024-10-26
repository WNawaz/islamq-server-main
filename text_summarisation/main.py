import time
import torch

from .model import AraBart, clean_text, summarizeText
from transformers import BartTokenizer, BartForConditionalGeneration

def load_arabart_model():
    print("Loading AraBart model")
    # log the model loading time
    start_time = time.time()
    trained_model = AraBart() 
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    trained_model.load_state_dict(torch.load('text_summarisation/model_weights.pth', map_location=device))
    print("AraBart model loaded")
    print("Time taken to load model: ", time.time() - start_time)
    return trained_model

def load_bart_model():
    print("Loading Bart model")
    # Load the BART model for summarization, log the time taken to load the model
    start_time = time.time()
    torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
    tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
    model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn').to(torch_device)
    print("Time taken to load model: ", time.time() - start_time)
    print("Bart model loaded")
    return tokenizer, model

def run_text_summarisation(text: str, language: str, trained_model, tokenizer, model):

    print("Text summarisation started")

    
    def inference_function():
        # Perform inference using the loaded models
        torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'

        if language == "arabic":
            cleaned_text = clean_text(text)
            result = list(map(lambda tex: summarizeText(tex, trained_model.model), cleaned_text))
            summary = '\n'.join(result)
            data = {'summary' : summary}
            return data
        elif language == "english":
            article_input_ids = tokenizer.batch_encode_plus([text], return_tensors='pt', max_length=1024)['input_ids'].to(torch_device)
            summary_ids = model.generate(article_input_ids,
                                    num_beams=4,
                                    length_penalty=2.0,
                                    max_length=1000,
                                    #  min_len=56,
                                    no_repeat_ngram_size=3)

            summary_txt = tokenizer.decode(summary_ids.squeeze(), skip_special_tokens=True)
            print(summary_txt)
            data = {'summary' : summary_txt}
            return data

    data = inference_function()
        
    # Summarise the data
    print("Text summarisation completed successfully!")

    return data
