import speech_recognition as sr
import pyttsx3
import re

# Inicializar el motor de síntesis de voz
engine = pyttsx3.init()

# Configuración de voces disponibles (opcional)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Cambiar el índice para seleccionar una voz diferente

# Función para que el asistente hable
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Expresiones regulares para coincidencia parcial
pattern_clima = re.compile(r"\b(clima|tiempo|pronóstico)\b", re.IGNORECASE)
pattern_saludo = re.compile(r"\b(hola|buenos días|buenas tardes|buenas noches)\b", re.IGNORECASE)
pattern_despedida = re.compile(r"\b(adiós|hasta luego|chao)\b", re.IGNORECASE)

# Función para procesar la consulta del usuario y generar una respuesta
def process_query(query):
    if pattern_clima.search(query):
        return "Veo que estás interesado en el clima. ¿Sobre qué ciudad te gustaría saber?"
    elif pattern_saludo.search(query):
        return "¡Hola! ¿En qué puedo ayudarte?"
    elif pattern_despedida.search(query):
        return "¡Hasta luego! Que tengas un buen día."
    else:
        return "Lo siento, no entendí eso. ¿Puedes repetir?"

# Función para escuchar al usuario y manejar errores de escucha
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Di algo...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        print("Reconociendo...")
        query = recognizer.recognize_google(audio, language='es')
        print(f"¿Has dicho: {query}?")
        speak(f"¿Has dicho: {query}?")
        return query.lower()
    except sr.UnknownValueError:
        print("Lo siento, no pude entender lo que dijiste. ¿Puedes repetir?")
        speak("Lo siento, no pude entender lo que dijiste. ¿Puedes repetir?")
        return ""
    except sr.RequestError as e:
        print(f"Error al solicitar resultados; {e}")
        speak(f"Error al solicitar resultados; {e}")
        return ""

# Programa principal
if __name__ == "__main__":
    print("Hola, soy tu asistente de voz. ¿En qué puedo ayudarte?")
    speak("Hola, soy tu asistente de voz. ¿En qué puedo ayudarte?")
    while True:
        query = listen()
        if query:
            response = process_query(query)
            print(response)
            speak(response)