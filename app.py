from nltk.corpus import wordnet
import random
import regex
from nltk.corpus import stopwords
import traceback
import os
import requests
import json
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, jsonify
import nltk
import os, requests, time
from xml.etree import ElementTree
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('wordnet')

app = Flask(__name__)

load_dotenv()

subscription_key = "b47284484d65447099dfca36649c87f2"

class TextToSpeech(object):
    def __init__(self, subscription_key, text):
        self.subscription_key = subscription_key
        self.tts = text
        self.timestr = time.strftime("%Y%m%d-%H%M")
        self.access_token = None

    '''
    The TTS endpoint requires an access token. This method exchanges your
    subscription key for an access token that is valid for ten minutes.
    '''
    def get_token(self):
        fetch_token_url = "https://centralindia.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        self.access_token = str(response.text)

    def save_audio(self):
        base_url = 'https://centralindia.tts.speech.microsoft.com/'
        path = 'cognitiveservices/v1'
        constructed_url = base_url + path
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
            'User-Agent': 'YOUR_RESOURCE_NAME'
        }
        xml_body = ElementTree.Element('speak', version='1.0')
        xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-us')
        voice = ElementTree.SubElement(xml_body, 'voice')
        voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-US')
        voice.set('name', 'en-US-Guy24kRUS') # Short name for 'Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)'
        voice.text = self.tts
        body = ElementTree.tostring(xml_body)

        response = requests.post(constructed_url, headers=headers, data=body)
        '''
        If a success response is returned, then the binary audio is written
        to file in your working directory. It is prefaced by sample and
        includes the date.
        '''
        if response.status_code == 200:
            with open('static/audio.wav', 'wb') as audio:
                audio.write(response.content)
                print("\nStatus code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")
        else:
            print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
            print("Reason: " + str(response.reason) + "\n")

def quizy(text):
    stop_words = set(stopwords.words('english'))
    lines = text
    sentences = nltk.sent_tokenize(lines)
    words = []
    q = []
    for sentence in sentences:
        if not sentence in stop_words:
            for word, pos in nltk.pos_tag(nltk.word_tokenize(str(sentence))):
                if (pos == 'JJ' or pos == 'RB'):
                    w = regex.sub(r'[^\w\s_]+', '', word).strip()
                    q.append(sentence.replace(w, "_____") + ": " + w)
                    words.append(w)
    questions = []
    q = random.sample(q, 5)
    for qq in q:
        questions.append(qq + "," + ",".join(random.sample(words, 3)))
    return questions


def makequiz(text):
    stop_words = set(stopwords.words('english'))
    lines = text
    sentences = nltk.sent_tokenize(lines)
    words = []

    for sentence in sentences:
        if not sentence in stop_words:
            for word, pos in nltk.pos_tag(nltk.word_tokenize(str(sentence))):
                if (pos == 'JJ'):
                    words.append(regex.sub(r'[^\w\s_]+', '', word).strip())

    words = list(set(words))
    questions = []
    synonyms_rolling = []
    antonyms_rolling = []

    for word in words:
        try:
            # print(word)
            synonyms = []
            antonyms = []
            synset = wordnet.synsets(word)
            # print(synset[0].definition())
            for syn in synset:
                for l in syn.lemmas():
                    synonyms.append(l.name().replace("_"," ").strip())
                    synonyms_rolling.append(l.name().replace("_"," ").strip())
                    if l.antonyms():
                        antonyms.append(l.antonyms()[0].name().replace("_"," ").strip())
                        antonyms_rolling.append(l.antonyms()[0].name().replace("_"," ").strip())
            # print(set(synonyms))
            # print(set(antonyms))
            # print("------------------------")
            if(len(set(synonyms)) > 0):
                questions.append(
                    f"The word '{word}' in the passage is closest in meaning to: {random.sample(list(set(synonyms)), 1)[0]}")
            if(len(set(antonyms)) > 0):
                questions.append(
                    f"The word '{word}' in the passage is opposite in meaning to: {random.sample(list(set(antonyms)), 1)[0]}")
            questions.append(
                f"Which word in the passage will be appropriate for the meaning '{synset[0].definition()}': {word}")
        except:
            continue
    questions = random.sample(list(questions), 5)
    final = []
    for question in questions:
        final.append(question + "," + ",".join(random.sample(synonyms_rolling + antonyms_rolling + words, 3)))
    return final


@app.route('/reading')
def reading():
    'Show the reading section'

    with open("sample.txt", "r+") as file:
        body = file.read()
    quiz = ""
    answer = ""
    for i, q in enumerate(makequiz(body)):
        quiz = quiz + "<p>" + str(q).split(":")[0] + "</p>"
        choices = str(q).split(":")[1].strip().split(",")
        answer = answer + "<div id='choice"+str(i)+"'>"+choices[0]+"</div>"
        for choice in random.sample(choices, len(choices)):
            quiz = quiz + "<div class='radio'><label><input type='radio' name='choice"+str(i)+"'>"+choice+"</label></div>"
        quiz = quiz + "<br>"
    return render_template('reading.html', body = body, quiz = quiz, answer = answer)


@app.route('/listening')
def listening():
    'Show the listening section'

    with open("listening.txt", "r+") as file:
        text = file.read()
    app = TextToSpeech(subscription_key, text)
    app.get_token()
    app.save_audio()
    quiz = ""
    answer = ""
    for i, q in enumerate(quizy(text)):
        quiz = quiz + "<p>" + str(q).split(":")[0] + "</p>"
        choices = str(q).split(":")[1].strip().split(",")
        answer = answer + "<div id='choice"+str(i)+"'>"+choices[0]+"</div>"
        for choice in random.sample(choices, len(choices)):
            quiz = quiz + "<div class='radio'><label><input type='radio' name='choice"+str(i)+"'>"+choice+"</label></div>"
        quiz = quiz + "<br>"
    return render_template('listening.html', quiz = quiz, answer = answer)


@app.route('/GetTokenAndSubdomain', methods=['GET'])
def getTokenAndSubdomain():
    'Get the access token'
    if request.method == 'GET':
        try:
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            data = {
                'client_id': str(os.environ.get('CLIENT_ID')),
                'client_secret': str(os.environ.get('CLIENT_SECRET')),
                'resource': 'https://cognitiveservices.azure.com/',
                'grant_type': 'client_credentials'
            }

            resp = requests.post('https://login.windows.net/' + str(
                os.environ.get('TENANT_ID')) + '/oauth2/token', data=data, headers=headers)
            jsonResp = resp.json()

            if ('access_token' not in jsonResp):
                print(jsonResp)
                raise Exception('AAD Authentication error')

            token = jsonResp['access_token']
            subdomain = str(os.environ.get('SUBDOMAIN'))

            return jsonify(token=token, subdomain=subdomain)
        except Exception as e:
            message = 'Unable to acquire Azure AD token. Check the debugger for more information.'
            print(message, e)
            return jsonify(error=message)
