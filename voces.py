import pyttsx3
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[20].id)
engine.say('¡Hola! Soy Lopako, tu asistente robótico personal diseñado para ayudarte a recordar cosas importantes y facilitar tu día a día. Mi objetivo es estar siempre a tu lado para apoyarte en todo momento.')
print(voices[20].id)
engine.runAndWait()
