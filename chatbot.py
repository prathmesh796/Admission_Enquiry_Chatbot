import random
import json
import pickle
import numpy as np
import nltk
import os
from dotenv import load_dotenv
from google import genai
import config

from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

# Load environment variables
load_dotenv()

lemmatizer = WordNetLemmatizer()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

intents = json.loads(open(os.path.join(BASE_DIR, "data/intents.json")).read())
words = pickle.load(open(os.path.join(BASE_DIR, "models/words.pkl"), "rb"))
classes = pickle.load(open(os.path.join(BASE_DIR, "models/classes.pkl"), "rb"))
model = load_model(os.path.join(BASE_DIR, "models/chatbot_model.h5"))

# Configure Google Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
gemini_client = None

if GEMINI_API_KEY and config.USE_GEMINI:
    try:
        # Initialize Gemini client with the new SDK
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        print("✓ Gemini AI integration enabled")
        print(f"✓ Using model: {config.GEMINI_MODEL}")
    except Exception as e:
        gemini_client = None
        print(f"✗ Gemini initialization failed: {e}")
else:
    if not GEMINI_API_KEY:
        print("✗ GEMINI_API_KEY not found in .env file")
    else:
        print("✗ Gemini features disabled in config")

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

def get_gemini_response(user_message, intent_info=None):
    """
    Generate enhanced response using Google Gemini AI
    """
    if not gemini_client:
        return None
    
    try:
        # Create context from intents.json
        context = "You are an admission chatbot for Marathwada Mitra Mandal's College of Engineering (MMCOE), Pune. "
        context += "You help students with admission queries and provide information about the college.\n\n"
        context += "Here is the college information database:\n"
        
        # Add relevant intent information as context
        for intent in intents['intents']:
            context += f"\nTopic: {intent['tag']}\n"
            if intent.get('responses'):
                context += f"Information: {intent['responses'][0]}\n"
        
        context += "\n\nIMPORTANT INSTRUCTIONS:\n"
        context += "1. Provide accurate, helpful, and friendly responses\n"
        context += "2. Keep responses concise but informative\n"
        context += "3. Use the college information provided above\n"
        context += "4. If you don't have specific information, guide the user to contact the college\n"
        context += "5. Maintain a professional yet friendly tone\n"
        context += "6. You can use HTML tags like <br> for line breaks and <a> for links if needed\n\n"
        
        # Add intent context if available
        if intent_info:
            context += f"\nThe user's query seems related to: {intent_info['intent']} "
            context += f"(confidence: {float(intent_info['probability']):.2%})\n\n"
        
        context += f"User Query: {user_message}\n\nResponse:"
        
        # Generate response using Gemini with the new SDK
        response = gemini_client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=context
        )
        return response.text
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None

def chatbot_response(msg):
    """
    Enhanced chatbot response with Gemini AI integration
    Supports multiple response modes based on config.RESPONSE_MODE
    """
    # Get intent prediction from the neural network
    ints = predict_class(msg, model)
    
    # Check if we have valid predictions
    if not ints or len(ints) == 0:
        # Use Gemini for completely unknown queries
        if gemini_client and config.USE_GEMINI:
            gemini_response = get_gemini_response(msg)
            if gemini_response:
                return gemini_response
        return "I'm not sure I understand. Could you please rephrase your question about MMCOE admissions?"
    
    # Get confidence level
    confidence = float(ints[0]['probability'])
    
    # Response mode logic
    if config.RESPONSE_MODE == 'traditional':
        # Traditional mode - always use neural network responses
        res = get_response(ints, intents)
        return res
    
    elif config.RESPONSE_MODE == 'gemini_all':
        # Gemini-all mode - always use Gemini for better responses
        if gemini_client:
            gemini_response = get_gemini_response(msg, ints[0])
            if gemini_response:
                return gemini_response
        # Fallback to traditional if Gemini fails
        res = get_response(ints, intents)
        return res
    
    else:  # hybrid mode (default)
        # Hybrid mode - use Gemini for low confidence, traditional for high confidence
        if confidence < config.CONFIDENCE_THRESHOLD and gemini_client:
            # Low confidence - use Gemini with intent hint
            gemini_response = get_gemini_response(msg, ints[0])
            if gemini_response:
                return gemini_response
        
        # High confidence - you can choose between traditional or Gemini
        # For best results, use Gemini even for high confidence
        if gemini_client:
            gemini_response = get_gemini_response(msg, ints[0])
            if gemini_response:
                return gemini_response
        
        # Fallback to traditional response
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
