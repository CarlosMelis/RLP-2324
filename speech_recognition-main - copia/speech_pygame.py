import pygame
import os
import glob
import time
from pocketsphinx import LiveSpeech, get_model_path
from enum import Enum
from untitled3_2 import *
from pyvidplayer2 import Video
import pyttsx3
import re

def speak(text):
    engine.say(text)
    engine.runAndWait()

class Tascas(Enum):
    Black = 0
    Intro = 1
    Main_Menu = 2
    Play = 3
    Remember = 4
    Off = 5
    
def fade(width, height, screen, image1, image2):
    for i in range(0, 255, 2):
        screen.fill((0,0,0))
        image1.set_alpha(255-i)
        image2.set_alpha(i)
        screen.blit(image1, (0,0))
        screen.blit(image2, (0,0))
        pygame.display.flip()
        pygame.time.delay(20)
        
def main_menu_func(carImg):
    carImg2 = pygame.image.load(os.path.join('init', "menu.png"))
    fade(1280, 720, gameDisplay, carImg, carImg2)
    pygame.display.update()
    audio_file = os.path.join(audio_dir, 'Home_Menu.mp3')
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    patterns() 
        
def juego_af():
    directorio = 'ejercicios\Atencion_focal'
    ruta_directorio = os.path.abspath(directorio)
    patrones = ['*.png']
    ex = []
    for patron in patrones:
        ex.extend(glob.glob(os.path.join(ruta_directorio, patron)))   
    for n, exercices in enumerate(ex):
        pygame.mixer.music.stop()
        #Habria que poner un tutorial de como funcionan los juegos
        carImg = pygame.image.load(os.path.join('', exercices))
        gameDisplay.blit(carImg, (0, 0))
        pygame.display.update()
        speak("De las imagenes de la derecha, ¿cual es igual a la numero 0?")
        acertado = False
        while not acertado:
            query = listen(tiempo_minimo=3, tiempo_maximo=3)
            if (n == 0) or (n == 1):
                if (re.compile(r"\b(cuatro|4)\b", re.IGNORECASE)).search(query):
                    speak("¡Muy bien! Has acertado. A por el siguiente.")
                    time.sleep(2)
                    acertado = True
                    break
                elif (re.compile(r"\b(uno|dos|tres|1|2|3)\b", re.IGNORECASE)).search(query):
                    speak("Ups. Me parece que es incorrecto.")
                    time.sleep(3)
                else:
                    speak("Lo siento. No te he entendido.")
                    time.sleep(1)
            if n == 2:
                if (re.compile(r"\b(dos|2)\b", re.IGNORECASE)).search(query):
                    speak("¡Muy bien! Has acertado. A por el siguiente.")
                    time.sleep(2)
                    acertado = True
                    break
                elif (re.compile(r"\b(uno|cuatro|tres|1|4|3)\b", re.IGNORECASE)).search(query):
                    speak("Ups. Me parece que es incorrecto.")
                    time.sleep(3)
                else:
                    speak("Lo siento. No te he entendido.")
                    time.sleep(1)
            if n == 3:
                if (re.compile(r"\b(tres|3)\b", re.IGNORECASE)).search(query):
                    speak("¡Muy bien! Has acertado.")
                    time.sleep(2)
                    acertado = True
                    break
                elif (re.compile(r"\b(uno|cuatro|dos|1|4|2)\b", re.IGNORECASE)).search(query):
                    speak("Ups. Me parece que es incorrecto.")
                    time.sleep(3)
                else:
                    speak("Lo siento. No te he entendido.")
                    time.sleep(1)
                    
    
    main_menu_func(carImg)
    
                
# Funciones para gestionar alarmas y temporizador (offline)
global alarma_activada

# Expresiones regulares para coincidencia parcial
pattern_consultar_hora = re.compile(r"\b(hora)\b", re.IGNORECASE)
pattern_consultar_evento = re.compile(r"\b((consultar|ver|revisar) (?:(?:los|las) )?eventos|calendario)\b", re.IGNORECASE)
pattern_agregar_evento = re.compile(r"\b((agregar|crear|insertar|añadir|añade) (?:(?:un|una) )?evento|nuevo evento)\b", re.IGNORECASE)
pattern_modificar_evento = re.compile(r"\b((modificar|editar|cambiar) (?:(?:un|una) )?evento|modificar evento)\b", re.IGNORECASE)
pattern_eliminar_evento = re.compile(r"\b((eliminar|quitar|borrar) (?:(?:un|una) )?evento|eliminar evento)\b", re.IGNORECASE)
pattern_mostrar_tareas = re.compile(r"\b((mostrar|ver|listar) (?:(?:las) )?tareas)\b", re.IGNORECASE)
pattern_agregar_tarea = re.compile(r"\b((agregar|crear|insertar|añadir|añade) (?:(?:una) )?tarea|nueva tarea)\b", re.IGNORECASE)
pattern_marcar_completada = re.compile(r"\b((marcar|checkear|completar) (?:(?:una) )?tarea|completar tarea)\b", re.IGNORECASE)
pattern_eliminar_tarea = re.compile(r"\b((eliminar|quitar|borrar) (?:(?:una) )?tarea|eliminar tarea)\b", re.IGNORECASE)
pattern_agregar_nota = re.compile(r"\b((agregar|crear|insertar|añadir|añade) (?:(?:una) )?nota|nueva nota)\b", re.IGNORECASE)
pattern_reproducir_nota = re.compile(r"\b((reproducir|escuchar|oir) (?:(?:una) )?nota|escuchar nota)\b", re.IGNORECASE)
pattern_eliminar_nota = re.compile(r"\b((eliminar|quitar|borrar) (?:(?:una) )?nota|eliminar nota)\b", re.IGNORECASE)
pattern_configurar_alarma = re.compile(r"\b(alarma)\b", re.IGNORECASE)
pattern_configurar_temporizador = re.compile(r"\b(temporizador|temporizar)\b", re.IGNORECASE)
pattern_configurar_contador = re.compile(r"\b(contar|cuenta|contador)\b", re.IGNORECASE)
pattern_juegos = re.compile(r"\b(jugar)\b", re.IGNORECASE)
pattern_back = re.compile(r"\b(atrás)\b", re.IGNORECASE)
pattern_af = re.compile(r"\b(atención|focal)\b", re.IGNORECASE)
pattern_bv = re.compile(r"\b(busqueda|visual)\b", re.IGNORECASE)
pattern_c = re.compile(r"\b(concentración)\b", re.IGNORECASE)
pattern_ayuda = re.compile(r"\b((ayuda|ayúdame|instrucciones|ayúdame por favor)|(consultar|ver|revisar) (?:ayuda|ayúdame|instrucciones|ayúdame por favor))\b", re.IGNORECASE)
pattern_saludo = re.compile(r"\b(hola|buenos días|buenas tardes|buenas noches)\b", re.IGNORECASE)
pattern_despedida = re.compile(r"\b(adiós|hasta luego|chao|nos vemos)\b", re.IGNORECASE)
        
def patterns():
    agenda = cargar_agenda()
    tareas = cargar_tareas()
    notas = cargar_notas()
    alarma_activada = False
    activacion = False

    while True:
        if not alarma_activada:
            query = listen(tiempo_minimo=3, tiempo_maximo=10)
            if query:                
                # Agenda y calendario
                if pattern_consultar_evento.search(query):
                    consultar_eventos(agenda)
                elif pattern_agregar_evento.search(query):
                    agregar_evento(agenda)
                elif pattern_modificar_evento.search(query):
                    modificar_evento(agenda)
                elif pattern_eliminar_evento.search(query):
                    eliminar_evento(agenda)
    
                # Listas de tareas
                elif pattern_mostrar_tareas.search(query):
                    mostrar_tareas(tareas)
                elif pattern_agregar_tarea.search(query):
                    agregar_tarea(tareas)
                elif pattern_marcar_completada.search(query):
                    marcar_tarea_como_completada(tareas)
                elif pattern_eliminar_tarea.search(query):
                    eliminar_tarea(tareas)
    
                # Notas de voz
                elif pattern_agregar_nota.search(query):
                    agregar_nota(notas)
                elif pattern_reproducir_nota.search(query):
                    reproducir_nota(notas)
                elif pattern_eliminar_nota.search(query):
                    eliminar_nota(notas)
    
                # Alarma y temporizador
                elif pattern_consultar_hora.search(query):
                    hora_actual = datetime.datetime.now().strftime("%H:%M")
                    print(f"La hora actual es {hora_actual}.")
                    speak(f"La hora actual es {hora_actual}.")
                elif pattern_configurar_alarma.search(query):
                    configurar_alarma()
                elif pattern_configurar_temporizador.search(query):
                    configurar_temporizador()
                elif pattern_configurar_contador.search(query):
                    configurar_contador()
                    
                # Juegos y entretenimiento
                elif pattern_juegos.search(query):
                    carImg = pygame.image.load(os.path.join('ejercicios', "menu_juegos.png"))
                    gameDisplay.blit(carImg, (0, 0))
                    pygame.display.update()
                    
                elif pattern_back.search(query):
                    carImg_Ant = pygame.image.load(os.path.join('init', "menu.png"))
                    gameDisplay.blit(carImg_Ant, (0, 0))
                    pygame.display.update()
                    
                elif pattern_af.search(query):
                    juego_af()
                    
                elif pattern_bv.search(query):
                    juego_bv()
                    
                elif pattern_c.search(query):
                    juego_c()
    
                # Despedida
                elif pattern_despedida.search(query):
                    print("¡Hasta luego! Que tengas un buen día.")
                    speak("¡Hasta luego! Que tengas un buen día.")
                    activacion = False
    
                # Ayuda
                elif pattern_ayuda.search(query):
                    ayuda()
                    
                # Procesamiento de consultas generales
                elif pattern_saludo.search(query):
                    print("¡Hola! ¿En qué puedo ayudarte?")
                    speak("¡Hola! ¿En qué puedo ayudarte?")
                
                else:
                    print("Lo siento, no entendí eso. ¿Puedes repetir?")
                    speak("Lo siento, no entendí eso. ¿Puedes repetir?")
                    continue
                
                activacion = False
        else:
            print("¡Alarma!")
            speak("¡Alarma!")
            time.sleep(0.5)
            print("¡Alarma!")
            speak("¡Alarma!")
            time.sleep(0.5)
            print("¡Alarma!")
            speak("¡Alarma!")
            time.sleep(0.5)
            # Aquí podría agregar la reproducción de un sonido de alarma o cualquier otra acción que desee.
            parar = listen(tiempo_minimo=1, tiempo_maximo=1)
            if parar == "para":
                print("Alarma detenida.")
                speak("Alarma detenida.")
                alarma_activada = False


# Define la ruta al modelo de reconocimiento de voz
model_path = "./vosk-model-small-es-0.42"
# Carga el modelo de reconocimiento de voz
model = vosk.Model(model_path)
# Configura la configuración de PyAudio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
# Inicia PyAudio
audio = pyaudio.PyAudio()
# Abre el stream de audio desde el micrófono
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
# Crea un reconocedor de voz utilizando el modelo especificado
recognizer = vosk.KaldiRecognizer(model, RATE)

pygame.init()
gameDisplay = pygame.display.set_mode((1280, 720))
state = Tascas.Black.value
menu = [x for x in glob.glob("init\\*.PNG")]
audio_dir = 'audios'
model_path = get_model_path()
running = True

while running:
    match state:
        case Tascas.Black.value:
            carImg = pygame.image.load(os.path.join('init', "black.png"))
            gameDisplay.blit(carImg, (0, 0))
            pygame.display.update()
            acertado = False
            while not acertado:
                query = listen(tiempo_minimo=3, tiempo_maximo=3)
                if pattern_activacion.search(query):
                    acertado = True
                    state = Tascas.Intro.value                   
        
        case Tascas.Intro.value:
            carImg = pygame.image.load(os.path.join('init', "black_logo.png"))
            gameDisplay.blit(carImg, (0, 0))
            pygame.display.update()
            audio_file = os.path.join(audio_dir, 'encendido.mp3')
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            time.sleep(3)
            state = Tascas.Main_Menu.value
            
             
        case Tascas.Main_Menu.value:
             main_menu_func(carImg)     

pygame.quit()
