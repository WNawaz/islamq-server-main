import requests

# Endpoint URLs
summarize_arabic_url = "http://localhost:4000/summarizeArabic"
summarize_english_url = "http://localhost:4000/summarizeEnglish"
search_english_data_url = "http://localhost:4000/search-english-data/"
search_arabic_data_url = "http://localhost:4000/search-arabic-data/"

# Example text for summarization
text_to_summarize = "This is an example text for summarization."
arabic_text_to_summarise = "في زمن مضى، في بلدة صغيرة على ضفاف النيل، كان هناك شاب يُدعى أحمد. كان أحمد شابًا طموحًا يحلم بتحقيق النجاح في حياته. ومنذ صغره، كان يحب القراءة واكتساب المعرفة. كان يمضي ساعات طويلة في مكتبته الصغيرة، يستمتع بقراءة الكتب واستكشاف عوالم جديدة. وفي يوم من الأيام، وقعت أحمد في غرام فتاة جميلة تُدعى ليلى. كانت ليلى ذات شخصية ساحرة وذكاء فائق. وكانت لقاؤهما الأول هو بداية قصة حب رائعة. عاش أحمد وليلى الكثير من اللحظات السعيدة معًا، وتجاوزوا العديد من التحديات والصعوبات. وفي يومٍ مشمس، قرر أحمد أن يتقدم بطلب للزواج من ليلى. وبعد فترة من التفكير، وافقت ليلى على الزواج من أحمد. واحتفلوا بحفل زفاف رائع وسط أجواء من الفرح والبهجة. وبهذا، بدأت رحلة جديدة لأحمد وليلى، مليئة بالحب والأمل والتفاؤل."

# Example query model for search endpoints
query_model = {
    "query": "example query",
    "k": 5  # Example value for 'k'
}

# Call summarizeArabic endpoint
response = requests.post(summarize_arabic_url, params={"text": arabic_text_to_summarise})
print("Summarize Arabic Response:", response.json())

# Call summarizeEnglish endpoint
response = requests.post(summarize_english_url, params={"text": text_to_summarize})
print("Summarize English Response:", response.json())

# Call search-english-data endpoint
response = requests.post(search_english_data_url, json=query_model)
print("Search English Data Response:", response.json())

# Call search-arabic-data endpoint
response = requests.post(search_arabic_data_url, json=query_model)
print("Search Arabic Data Response:", response.json())
