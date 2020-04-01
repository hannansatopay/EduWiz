import random
import regex
from nltk.corpus import wordnet
from nltk.corpus import stopwords
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('wordnet')


def quizy(type, text):
    words = []
    qq = []
    questions = []
    synonyms_rolling = []
    antonyms_rolling = []
    quiz = answer = ""
    stop_words = set(stopwords.words('english'))
    lines = text
    sentences = nltk.sent_tokenize(lines)

    # Quiz Type: Generate Fill in the Blanks
    if type == "fib":
        for sentence in sentences:
            if not sentence in stop_words:
                for word, pos in nltk.pos_tag(nltk.word_tokenize(str(sentence))):
                    if (pos == 'JJ' or pos == 'RB'):
                        w = regex.sub(r'[^\w\s_]+', '', word).strip()
                        qq.append(sentence.replace(w, "_____") + ": " + w)
                        words.append(w)
        qq = random.sample(qq, 5)
        for q in qq:
            questions.append(q + "," + ",".join(random.sample(words, 3)))

    # Quiz Type: Generate antonyms, synonyms and meaning
    elif type == "asm":
        for sentence in sentences:
            if not sentence in stop_words:
                for word, pos in nltk.pos_tag(nltk.word_tokenize(str(sentence))):
                    if (pos == 'JJ'):
                        words.append(regex.sub(r'[^\w\s_]+', '', word).strip())
        words = list(set(words))
        for word in words:
            try:
                synonyms = []
                antonyms = []
                synset = wordnet.synsets(word)
                for syn in synset:
                    for l in syn.lemmas():
                        synonyms.append(l.name().replace("_", " ").strip())
                        synonyms_rolling.append(
                            l.name().replace("_", " ").strip())
                        if l.antonyms():
                            antonyms.append(
                                l.antonyms()[0].name().replace("_", " ").strip())
                            antonyms_rolling.append(
                                l.antonyms()[0].name().replace("_", " ").strip())
                if(len(set(synonyms)) > 0):
                    qq.append(f"The word '{word}' in the passage is closest in meaning to: {random.sample(list(set(synonyms)), 1)[0]}")
                if(len(set(antonyms)) > 0):
                    qq.append(f"The word '{word}' in the passage is opposite in meaning to: {random.sample(list(set(antonyms)), 1)[0]}")
                qq.append(f"Which word in the passage will be appropriate for the meaning '{synset[0].definition()}': {word}")
            except:
                continue
        qq = random.sample(list(qq), 5)
        for q in qq:
            questions.append(q + "," + ",".join(random.sample(synonyms_rolling + antonyms_rolling + words, 3)))

    # Generate the appropriate HTML for the quiz
    for i, value in enumerate(questions):
        quiz = quiz + "<p>" + str(value).split(":")[0] + "</p>"
        choices = str(value).split(":")[1].strip().split(",")
        answer = answer + "<div id='choice" + str(i) + "'>" + choices[0] + "</div>"
        for choice in random.sample(choices, len(choices)):
            quiz = quiz + "<div class='radio'><label><input type='radio' name='choice" + str(i) + "'>" + choice + "</label></div>"
        quiz = quiz + "<br>"

    return (quiz, answer)
