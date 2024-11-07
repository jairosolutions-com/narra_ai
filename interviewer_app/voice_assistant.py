# assistant/voice_assistant.py
import speech_recognition as sr
import pyttsx3


def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for speech...")
        audio = recognizer.listen(source)

    try:
        # Using Google Web Speech API for recognition
        print("Recognizing speech...")
        return recognizer.recognize_google(audio)
    except sr.RequestError:
        # API error
        return "API request error"
    except sr.UnknownValueError:
        # Speech not recognized
        return "Sorry, I didn't understand that."


def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
