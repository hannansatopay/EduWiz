import json
import requests
from azure.ai.textanalytics import TextAnalyticsClient, TextAnalyticsApiKeyCredential


def authenticate_client(key, endpoint):
    ta_credential = TextAnalyticsApiKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint, credential=ta_credential)
    return text_analytics_client


def sentiment_analysis(client, text):
    response = client.analyze_sentiment(inputs=[text])[0]
    return response.sentiment


def key_phrase_extraction(client, text):
    response = client.extract_key_phrases(inputs=[text])[0]
    return response.key_phrases


def spellcheck(key, endpoint, text):
    data = {'text': text}
    params = {'mkt': 'en-us', 'mode': 'proof'}
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Ocp-Apim-Subscription-Key': key}
    response = requests.post(endpoint, headers=headers,
                             params=params, data=data)
    result = response.json()
    return result
