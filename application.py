import random
import requests
import json
from flask import Flask, redirect, render_template, request, jsonify
import azurespeech  # Custom module created for text to speech
from quizy import quizy  # Custom module created to automatically generate quiz
# Custom module created to consume text analytics capabilities of Azure
from azuretextanalytics import authenticate_client, sentiment_analysis, key_phrase_extraction, spellcheck

# Environment Variables
## Immersive Reader
tenant_id = "2feb31ec-24c0-4f0e-8ee7-7bf3b3585b79"
subdomain = "Speedster"
client_id = "6ac840a0-7415-4e3b-98b1-28fc2424bc43"
client_secret = "CromptonGreaves007@"

## Speech API
subscription_key = "b47284484d65447099dfca36649c87f2"
service_region = "centralindia"

## Text Analytics API
text_analytics_key = "4f8b50dde4984fd6964f853450492c0e"
text_analytics_endpoint = "https://speedster-textanalytics.cognitiveservices.azure.com"

## Spell Check API
spell_check_key = "215e2ed917c1464293a3ed4066fa18c8"
spell_check_endpoint = "https://api.cognitive.microsoft.com/bing/v7.0/SpellCheck"


app = Flask(__name__)


@app.route('/')
def home():
    'Show the homepage'
    return render_template('home.html')


@app.route('/reading')
def reading():
    'Show the reading section'

    with open("reading.txt", "r+") as file:
        text = file.read()

    quiz, answer = quizy("asm", text)
    return render_template('reading.html', text = text, quiz = quiz, answer = answer)


@app.route('/listening')
def listening():
    'Show the listening section'

    with open("listening.txt", "r+") as file:
        text = file.read()

    speech = azurespeech.TextToSpeech(subscription_key, service_region, text)
    speech.get_token()
    speech.save_audio()
    quiz, answer = quizy("fib", text)
    return render_template('listening.html', quiz = quiz, answer = answer)


@app.route('/speaking')
def speaking():
    'Show the speaking section'

    question = '''Do you agree or disagree with the following statement?
    Overall, the widespread use of the internet has a mostly positive effect on life in today’s world.'''

    return render_template('speaking.html', question = question, key = subscription_key, region = service_region)


@app.route('/writing')
def writing():
    'Show the writing section'

    question = '''Do you agree or disagree with the following statement?
    Overall, the widespread use of the internet has a mostly positive effect on life in today’s world.'''

    return render_template('writing.html', question = question)


@app.route('/textanalytics/<section>', methods=['POST'])
def textanalytics(section):
    'Perform text analytics'

    text = request.form['text']
    display = "<h3>Total Words:</h3> <p>" + str(len(text.split())) + "</p>"
    display = display + "<h3>Total Words (Unique):</h3> <p>" + str(len(set(text.split()))) + "</p>"
    if section == "writing":
        spelling = spellcheck(spell_check_key, spell_check_endpoint, text)
        if(len(spelling["flaggedTokens"]) > 0):
            display = display + "<h3>Spelling Mistakes:</h3>"
            for token in spelling["flaggedTokens"]:
                display = display + "<p>" + token["token"] + " >>> " + token["suggestions"][0]["suggestion"] + "</p>"
    client = authenticate_client(text_analytics_key, text_analytics_endpoint)
    sentiment = sentiment_analysis(client, text)
    display = display + "<h3>Sentiment:</h3> <p>" + sentiment + "</p>"
    key_phrase = key_phrase_extraction(client, text)
    display = display + "<h3>Key Phrases:</h3> <p>" + str(key_phrase) + "</p>"
    return jsonify(display = display)


@app.route('/GetTokenAndSubdomain', methods=['GET'])
def getTokenAndSubdomain():
    'Get the access token for the Immersive Reader'
    if request.method == 'GET':
        try:
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'resource': 'https://cognitiveservices.azure.com/',
                'grant_type': 'client_credentials'
            }

            resp = requests.post('https://login.windows.net/' +
                                 tenant_id + '/oauth2/token', data=data, headers=headers)
            jsonResp = resp.json()

            if ('access_token' not in jsonResp):
                print(jsonResp)
                raise Exception('AAD Authentication error')

            token = jsonResp['access_token']

            return jsonify(token=token, subdomain=subdomain)
        except Exception as e:
            message = 'Unable to acquire Azure AD token. Check the debugger for more information.'
            print(message, e)
            return jsonify(error=message)
