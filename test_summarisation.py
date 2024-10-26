# write test requests for the summarisation API

import requests

def test_summarise_arabic():
    url = "http://localhost:7000/summarizeArabic"
    data = {
        "text": "السلام عليكم ورحمة الله وبركاته"
    }
    response = requests.post(url, params=data)  # Fixed line
    assert response.status_code == 200
    
    # format the response to match utf-8 encoding
    response.encoding = 'utf-8'
    print(response.text)
    # assert response.json() == {'summary': 'السلام عليكم ورحمة الله وبركاته'}

def test_summarise_english():
    url = "http://localhost:7000/summarizeEnglish"
    data = {
        "text": "Hello, how are you doing today?"
    }
    response = requests.post(url, params=data)
    assert response.status_code == 200
    print(response.text)
    # assert response.json() == {'summary': 'Hello, how are you doing today?'}

test_summarise_arabic()
test_summarise_english()
