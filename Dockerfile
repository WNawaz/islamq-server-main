# 
FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN apt-get update && apt-get install -y python3 python3-pip && \
    pip3 install --upgrade pip && \
    pip3 install gdown && \
    pip3 install --no-cache-dir --upgrade -r /code/requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 
COPY ./controller.py /code
COPY ./arabic_scraper /code/arabic_scraper
COPY ./data /code/data
COPY ./server /code/server
COPY ./speech_recognition /code/speech_recognition
COPY ./text_summarisation /code/text_summarisation
COPY ./translation /code/translation

#download models
RUN gdown --id 1fCA-ECnHykbTaueCsfQ-N2mf2YboYI7A -O /code/text_summarisation/model_weights.pth

# 
EXPOSE 4000
CMD ["python3", "controller.py", "--port", "4000"]

