import random
import json
import pickle
import numpy as np
import nltk
import os

from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

lemmatizer = WordNetLemmatizer()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

intents = json.loads(open(os.path.join(BASE_DIR, "intents.json")).read())
words = pickle.load(open(os.path.join(BASE_DIR, "words.pkl"), "rb"))
classes = pickle.load(open(os.path.join(BASE_DIR, "classes.pkl"), "rb"))
model = load_model(os.path.join(BASE_DIR, "chatbot_model.h5"))

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words

def bag_of_words (sentence, show_details = True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)

def predict_class (sentence, model):
    bow = bag_of_words (sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes [r[0]], 'probability': str(r[1])})
    return return_list

def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice (i['responses'])
            break

    return result


def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = get_response(ints, intents)
    return res

#flask app
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def get_index():
    return render_template("base.html")

@app.route('/get')
def get_bot_response():
        key = request.args.get('msg')
        return chatbot_response(key)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
