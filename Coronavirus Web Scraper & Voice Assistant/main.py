#importing modules/libraries

import requests
import json
import pyttsx3  #speech
import speech_recognition as sr  #speech
import re   #REgEX
import threading  #use to run multiple task at a time
import time

#parserhub API data

API_KEY = " {PUT YOUR VALUE} "
PROJECT_TOKEN = " {PUT YOUR VALUE} "
RUN_TOKEN = " {PUT YOUR VALUE} "



class Data:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {                     #for authentication
            "api_key" : self.api_key
        }
        self.data = self.get_data()

#helps to have a look at parsehub more clearly
#parserhub is used to scarp data  from site : https://www.mygov.in/corona-data/covid19-statewise-status/
    def get_data(self):
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data',params=self.params)
        data = json.loads(response.text)
        return data

# for extracting total cases till date
    def get_total_cases(self):
        data = self.data ['total']

        for content in data:
            if content['name'] == "Active Cases:":    # if name is Active Case its value will be extracted
                return content['value']

# for extracting total death cases till dates
    def get_total_deaths(self):
        data = self.data ['total']

        for content in data:
            if content['name'] == "Deaths:":    #if name is Deaths then its value will be extracted
                return content['value']

# for extracting total recovered cases till dates
    def get_total_recovered(self):
        data = self.data ['total']

        for content in data:
            if content['name'] == "Cured/Discharged:":  #if name is Cured/Discharged then its value will be extracted
                return content['value']

# for extracting state wise data
    def get_states_data (self, states):
        data = self.data["states"]

        for contents in data:
            if contents['name'].lower() == states.lower():   #all string is converted into lower
                return contents
        return "0"

# for extracting list of state present
    def get_lists_of_state(self):
        state = []     # create list
        for states in self.data['states']:
            state.append(states['name'].lower())
        return state

#for updating the site if any changes

    def update_data(self):
        response = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run', params=self.params)


        def poll():
            time.sleep(0.1)
            old_data = self.data
            while True:
                new_data = self.get_data()
                if new_data != old_data:
                    self.data = new.data
                    print("Data Updated")
                    break
                time.sleep(5)     #after every 5 sec check of new if got stop the def


        t = threading.Thread(target=poll)
        t.start()

#data = Data(API_KEY, PROJECT_TOKEN)
#print(data.get_states_data("maharashtra")["total_cases"])
#print(data.get_lists_of_state())

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

#speak("Hello")

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)  #record the audio and store temporarily
        said = ""

        try:
            said = r.recognize_google(audio)
        except Exception as e:
            print ("Exception:", str(e))

    return said.lower()

def main():
    print ("Started Program")
    data = Data(API_KEY, PROJECT_TOKEN)
    END_PHRASE = "stop"   #if said the program will terminate
    states_list = data.get_lists_of_state()

#REgex patter, if such pattern is seen than that search is runned
#\w\s it means - which matches one character which does not belong to either the word or the whitespace group
    TOTAL_PATTERNS = {
                      re.compile("[\w\s]+ total [\w\s]+ cases"): data.get_total_cases,        #EXAMple: How many total number of cases:
                      re.compile("[\w\s]+ total cases"): data.get_total_cases,
                      re.compile("[\w\s]+ total [\w\s]+ deaths"): data.get_total_deaths,
                      re.compile("[\w\s]+ total deaths"): data.get_total_deaths,
                      re.compile("[\w\s]+ total [\w\s]+ recovered"): data.get_total_recovered,
                      re.compile("[\w\s]+ total recovered"): data.get_total_recovered,

    }

    STATES_PATTERNS = {
					re.compile("[\w\s]+ cases [\w\s]+"): lambda states: data.get_states_data(states)['total_cases'],
                    re.compile("[\w\s]+ died [\w\s]+"): lambda states: data.get_states_data(states)['total_deaths'],
                    re.compile("[\w\s]+ recovered [\w\s]+"): lambda states: data.get_states_data(states)['total_recovered'],
					}

    UPDATE_COMMAND = "update"

    while True:
        print("Listening...")
        text = get_audio()
        print ("You Said: ",text)
        result = None

        for pattern, func in STATES_PATTERNS.items():
            if pattern.match(text):
                words = set(text.split(" "))    #"How many cases in goa"  {"How", "many","cases","in","goa"}
                for states in states_list:
                    if states in words:
                        result = func(states)
                        break

        for pattern, func in TOTAL_PATTERNS.items():
            if pattern.match(text):
                result = func()
                break

        if text == UPDATE_COMMAND:
            result = "Data is being Updated. This may take a Moment!!"
            data.update_data()

        if result:
            speak(result)
            print(result)

        if text.find(END_PHRASE) !=-1:        #stop loop  #!= -1 will ensure that it will not get terminated on it owns
            print("Exit")
            break
main()
