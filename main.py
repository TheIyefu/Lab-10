import requests
import pyttsx3
import os
import pyaudio
from vosk import Model, KaldiRecognizer

# Initialize pyttsx3 speech synthesis engine
engine = pyttsx3.init()

# Initialize Vosk speech recognition model
model = Model("model")
rec = KaldiRecognizer(model, 16000)

# Set up the API endpoint
api_url = "https://rickandmortyapi.com/api/character/"

def recognize_speech():
    # Set up audio recording
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()
    
    # Collect audio data
    frames = []
    while True:
        data = stream.read(2000, exception_on_overflow=False)
        if len(data) == 0:
            break
        frames.append(data)

    # Recognize speech
    stream.stop_stream()
    stream.close()
    p.terminate()

    data = b''.join(frames)
    if len(data) > 0:
        if rec.AcceptWaveform(data):
            result = rec.Result()
            return result

    return None

def speak(text):
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()

def get_random_character():
    response = requests.get(api_url + "random")
    data = response.json()
    if response.status_code == 200:
        character_name = data["name"]
        return character_name
    else:
        return None

def save_character_picture(character_id):
    response = requests.get(api_url + str(character_id))
    data = response.json()
    if response.status_code == 200:
        character_name = data["name"]
        image_url = data["image"]
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            os.makedirs("character_pictures", exist_ok=True)
            with open(f"character_pictures/{character_name}.jpg", 'wb') as file:
                file.write(response.content)
            return True
    return False

def get_episode(character_id):
    response = requests.get(api_url + str(character_id))
    data = response.json()
    if response.status_code == 200:
        episode_name = data["episode"][0]
        response = requests.get(episode_name)
        data = response.json()
        if response.status_code == 200:
            episode = data["name"]
            return episode
    return None

def display_picture(character_id):
    response = requests.get(api_url + str(character_id))
    data = response.json()
    if response.status_code == 200:
        character_name = data["name"]
        image_url = data["image"]
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(f"{character_name}.jpg", 'wb') as file:
                file.write(response.content)
            os.system(f"start {character_name}.jpg")
            return True
    return False

if __name__ == "__main__":
    while True:
        command = recognize_speech()
        if command:
            command = command.lower().strip()

            if "random" in command:
                character_name = get_random_character()
                if character_name:
                    speak(f"The random character is {character_name}")
                else:
                    speak("Error retrieving the random character")

            elif "save" in command:
                character_id = int(command.split()[-1])
                if save_character_picture(character_id):
                    speak("Picture saved successfully")
                else:
                    speak("Error saving the picture")

            elif "episode" in command:
                character_id = int(command.split()[-1])
                episode = get_episode(character_id)
                if episode:
                    speak(f"The episode of the first appearance is {episode}")
                else:
                    speak("Error retrieving the episode")

            elif "show" in command:
                character_id = int(command.split()[-1])
                if display_picture(character_id):
                    speak("Picture displayed successfully")
                else:
                    speak("Error displaying the picture")

            elif "resolution" in command:
                speak("The resolution is 1920 by 1080 pixels")

            else:
                speak("Command not recognized")

        else:
            speak("Error in speech recognition")
