import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy
import tflearn
import tensorflow
from tensorflow.python.framework import ops
import random
import json
import pickle
import os
import sys
import requests
import time
import playsound
import speech_recognition as sr
from gtts import gTTS


nltk.download("punkt")

def speak(text):
    tts = gTTS(text=text, lang="en")
    filename = "voice.mp3"
    tts.save(filename)
    playsound.playsound(filename)

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""
        
        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            print("Exception: " + str(e))

    return said

text = get_audio()

def function():
    print('test')

if "hello" in text:
    with open("intents.json") as file:
        data = json.load(file)
    ptint('Mental Health')

elif "bye" in text:
    with open('intent.json') as file:
        data = json.load(file)
    print('Convo Talk')

elif "water" in text:
    function()

else:
    return

try:
    with open("data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)

except: 
    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])

        if intent["tag"] not in labels:
            labels.append(intent["tag"])

    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []

        wrds = [stemmer.stem(w) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)


    training = numpy.array(training)
    output = numpy.array(output)

    with open("data.pickle", "wb") as f:
        pickle.dump((words, labels, training, output), f)

ops.reset_default_graph()

net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)

model.save("model.tflearn")

try:
    model.load("model.tflearn")
except:
    model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
    model.save("model.tflearn")

def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = (1)

    return numpy.array(bag)



def chat():
    print("Start Talking With the Bot! (type quit to stop)")      
    while True:
        def get_audio():
            r = sr.Recognizer()
            with sr.Microphone() as source:
                audio = r.listen(source)
                said = ""
                
                try:
                    said = r.recognize_google(audio)
                    print(said)
                    inp = said
                    if inp.lower() == "quit":
                        return

                    results = model.predict([bag_of_words(inp, words)])
                    results_index = numpy.argmax(results)
                    tag = labels[results_index]

                    for tg in data["intents"]:
                        if tg['tag'] == tag:
                            responses = tg['responses']

                    print(random.choice(responses))

                    def speak(text):
                        tts = gTTS(text=text, lang="en")
                        filename = "voice" + inp + ".mp3"
                        tts.save(filename)
                        playsound.playsound(filename)
                        os.remove(filename)

                    speak(random.choice(responses))
                except Exception as e:
                    print("Exception: " + str(e))
            return said

            text = get_audio()
        get_audio()
chat()