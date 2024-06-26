import vosk
import pyaudio
import pyttsx3
import re
import os
import datetime
import calendar
import pickle
import threading
import time
import numpy as np
from word2number_es import w2n
import tkinter as tk
from tkinter.font import Font
import sys
from playsound import playsound  
from PIL import Image, ImageTk  
import glob
import random
from PIL import Image, ImageTk
import cv2
import imutils
import capturandoRostros
import random
from ffpyplayer.player import MediaPlayer
import inspect
from tkinter import PhotoImage
import subprocess
import time
from time import sleep
from gpiozero import AngularServo 
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306                                                                                                                      

PWM_PIN = 12
global btn_jugar, btn_preguntas, btn_recuerda, btn_menu, alto, ancho, btn_siguiente, button_image, indice_pregunta, btn_pregunta_siguiente
global screen_width, screen_height                                                 
screen_width = 128
screen_height = 64
alto = 1024
ancho = 600
activacion_flag = False

def start_capturing():
    print("capturando")
    capturandoRostros.capturando_rostros()
    
def moverservo():
    servo = AngularServo(18, min_pulse_width=0.001, max_pulse_width=0.0023)

    servo.angle = 50.0
    sleep(0.5)
    servo.angle = 0.0
    sleep(0.5)
    servo.angle = -36.0
    sleep(0.5)
    servo.angle = 0.0
    sleep(0.5)
    servo.angle = 36.0


    
def speak(text):
    os.system(f'echo "{text}" | festival --tts --language spanish')
    
# Expresiones regulares para coincidencia parcial

# Reloj
pattern_consultar_hora = re.compile(r"\b(hora)\b", re.IGNORECASE)
pattern_configurar_alarma = re.compile(r"\b(alarma)\b", re.IGNORECASE)
pattern_configurar_temporizador = re.compile(r"\b(temporizador|temporizar)\b", re.IGNORECASE)
pattern_configurar_contador = re.compile(r"\b(contar|cuenta|contador)\b", re.IGNORECASE)

# Juegos y terapias
pattern_terapia = re.compile(r"\b(terapia)\b", re.IGNORECASE)
pattern_juegos = re.compile(r"\b(jugar|juego)\b", re.IGNORECASE)
pattern_remember = re.compile(r"\b(recordar)\b", re.IGNORECASE)
pattern_back = re.compile(r"\b(atrás)\b", re.IGNORECASE)
pattern_af = re.compile(r"\b(atención|focal)\b", re.IGNORECASE)
pattern_bv = re.compile(r"\b(busqueda|visual)\b", re.IGNORECASE)
pattern_c = re.compile(r"\b(concentración)\b", re.IGNORECASE)

# Otros
pattern_ayuda = re.compile(r"\b(ayuda|ayúdame|instrucciones)\b", re.IGNORECASE)
pattern_saludo = re.compile(r"\b(hola|buenos días|buenas tardes|buenas noches)\b", re.IGNORECASE)
pattern_despedida = re.compile(r"\b(adiós|hasta luego|chao|nos vemos)\b", re.IGNORECASE)
pattern_detener = re.compile(r"\b(para|basta|detente|termina)\b", re.IGNORECASE)

# Sistema
pattern_cambiar_color = re.compile(r"\b(cambiar|poner|configurar) ?(el|la)? (fondo|pantalla|tema) ?(a)?\b", re.IGNORECASE)
pattern_detener = re.compile(r"\b(para|basta|detente|termina|atras|retroceder|atrás|salir)\b", re.IGNORECASE)
pattern_siguiente = re.compile(r"\b(siguiente|pasar|próximo|continuar|adelante|avanzar)\b", re.IGNORECASE)

def ejecutar_juego_aleatorio():
    
    juegos = [juego_af, juego_c, juego_bv]
    juego_seleccionado = random.choice(juegos)
    juego_seleccionado()

def juego_af():
    def avanzar_ejercicio(correcto):
        nonlocal indice_ejercicio, acertado
        if correcto:
            if indice_ejercicio == len(ejercicios_respuestas) - 1:
                speak("Muy bien, has acertado. Ya no quedan mas problemas.")
                #btn_siguiente.place_forget()  # Ocultar el botón al finalizar todos los ejercicios
            else:
                speak("Muy bien, has acertado. A por el siguiente.")
            acertado = True
            indice_ejercicio += 1
        else:
            speak("Me parece que es incorrecto.")
    
    directorio = os.path.join('ejercicios', 'Atencion_focal')
    ruta_directorio = os.path.abspath(directorio)
    mostrar_ocultar_botones(False)
    patrones = ['*.png']
    ejercicios = []
    for patron in patrones:
        ejercicios.extend(glob.glob(os.path.join(ruta_directorio, patron)))
    
    ejercicios_respuestas = [
        {"imagen": "ejercicio1.png", "respuesta": 4},
        {"imagen": "ejercicio2.png", "respuesta": 4},
        {"imagen": "ejercicio3.png", "respuesta": 2},
        {"imagen": "ejercicio4.png", "respuesta": 3}
    ]

    ejercicios_respuestas = [er for er in ejercicios_respuestas if os.path.join(ruta_directorio, er["imagen"]) in ejercicios]
    random.shuffle(ejercicios_respuestas)
    
    indice_ejercicio = 0
    acertado = False
    
    def correct_answer():
        if indice_ejercicio < len(ejercicios_respuestas):
            avanzar_ejercicio(True)
        else:
            btn_siguiente.place_forget()

    
    while indice_ejercicio < len(ejercicios_respuestas):
        ejercicio = ejercicios_respuestas[indice_ejercicio]
        load_and_show_image(os.path.join(ruta_directorio, ejercicio["imagen"]))
        speak("De las imagenes de la derecha, cual es igual a la mostrada")
        acertado = False
        
        while not acertado:
            query = listen(tiempo_minimo=3, tiempo_maximo=3)
            
            if not query:
                continue
            
            if pattern_detener.search(query):
                return
            
            match = re.search(r"\b(\d+)\b", query)
            if not match:
                speak('Lo siento, no he escuchado bien el numero.')
                continue
            
            respuesta_usuario = int(match.group(1))
            avanzar_ejercicio(respuesta_usuario == ejercicio["respuesta"])
    
    main_loop(True)

def preguntas():
    global indice_pregunta, btn_pregunta_siguiente

    mostrar_ocultar_botones(False)
    preguntas_imagenes = [
        ("Como ha ido el dia", "PREGUNTA1.png"),
        ("Tienes hijos? Cuantos? Como se llaman?", "PREGUNTA2.png"),
        ("Cual es tu comida favorita? Quien la preparaba mejor?", "PREGUNTA3.png"),
        ("Que tipo de musica te gusta?", "PREGUNTA4.png"),
    ]
    btn_pregunta_siguiente.place(x=50, y=50)
    if indice_pregunta < len(preguntas_imagenes):
        pregunta, imagen = preguntas_imagenes[indice_pregunta]
        load_and_show_image(os.path.join('ejercicios', 'preguntas', imagen))
        speak(pregunta)
        indice_pregunta += 1
    else:
        finpreguntas()
        
def finpreguntas():
        global  btn_pregunta_siguiente
        speak("No hay mas preguntas. Que pases un buen dia.")
        btn_pregunta_siguiente.place_forget()
        main_loop(True)
        
def juego_bv():

    label_info.config(text="")
    directorio = 'ejercicios/Busqueda_visual'
    ruta_directorio = os.path.join(os.getcwd(), directorio)
    mostrar_ocultar_botones(False)
    # Obtener todas las imágenes en el directorio que terminan con .png, ordenadas por nombre
    imagenes = sorted([f for f in os.listdir(ruta_directorio) if f.endswith('.png')])
    
    for n, imagen in enumerate(imagenes):
        #Habria que poner un tutorial de como funcionan los juegos
        load_and_show_image(os.path.join(ruta_directorio, imagen))
        speak("Encuentra la figura que es igual a la del circulo de entre todas estas")
        acertado = False
        while not acertado:
            query = listen(tiempo_minimo=3, tiempo_maximo=3)
            if n == 0:
                if (re.compile(r"\b(cinco|5)\b", re.IGNORECASE)).search(query):
                    speak("Muy bien, has acertado. A por el siguiente.")
                    time.sleep(2)
                    acertado = True
                    break
                elif (re.compile(r"\b(uno|dos|tres|cuatro|seis|siete|ocho|nueve|diez|doce|1|2|3|4|6|7|8|9|10|12)\b", re.IGNORECASE)).search(query):
                    speak("Ups. Me parece que es incorrecto.")
                    time.sleep(3)
                else:
                    speak("Lo siento. No te he entendido.")
                    time.sleep(1)
            if n == 1:
                if (re.compile(r"\b(once|11)\b", re.IGNORECASE)).search(query):
                    speak("Muy bien, has acertado. A por el siguiente.")
                    time.sleep(2)
                    acertado = True
                    break
                elif (re.compile(r"\b(uno|dos|tres|cuatro|seis|siete|nueve|diez|cinco|doce|1|2|3|4|6|7|9|10|5|12)\b", re.IGNORECASE)).search(query):
                    speak("Ups. Me parece que es incorrecto.")
                    time.sleep(3)
                else:
                    speak("Lo siento. No te he entendido.")
                    time.sleep(1)
            if n == 2:
                if (re.compile(r"\b(ocho|8)\b", re.IGNORECASE)).search(query):
                    speak("Muy bien, has acertado. A por el siguiente.")
                    time.sleep(2)
                    acertado = True
                    break
                elif (re.compile(r"\b(uno|dos|tres|cuatro|seis|siete|cinco|nueve|diez|once|doce|1|2|3|4|6|7|5|9|10|11|12)\b", re.IGNORECASE)).search(query):
                    speak("Ups. Me parece que es incorrecto.")
                    time.sleep(3)
                else:
                    speak("Lo siento. No te he entendido.")
                    time.sleep(1)
            if n == 3:
                if (re.compile(r"\b(nueve|9)\b", re.IGNORECASE)).search(query):
                    speak("Muy bien, has acertado.")
                    time.sleep(2)
                    acertado = True
                    break
                elif (re.compile(r"\b(uno|dos|tres|cuatro|seis|siete|ocho|cinco|diez|once|doce|1|2|3|4|6|7|8|5|10|11|12)\b", re.IGNORECASE)).search(query):
                    speak("Ups. Me parece que es incorrecto.")
                    time.sleep(3)
                else:
                    speak("Lo siento. No te he entendido.")
                    time.sleep(1)
                    
    
    main_loop(True)
    
def juego_bv2():
    directorio = os.path.join('ejercicios', 'Busqueda_visual')
    ruta_directorio = os.path.abspath(directorio)
    patrones = ['*.png']
    ejercicios = []
    mostrar_ocultar_botones(False)
    for patron in patrones:
        ejercicios.extend(glob.glob(os.path.join(ruta_directorio, patron)))

    # Pares de imágenes y respuestas correctas (asegúrate de que estén en el mismo orden)
    # Formato: {"imagen": "ruta_imagen", "respuesta": respuesta_correcta}
    ejercicios_respuestas = [
        {"imagen": "ejercicio1.png", "respuesta": 5},
        {"imagen": "ejercicio2.png", "respuesta": 11},
        {"imagen": "ejercicio3.png", "respuesta": 8},
        {"imagen": "ejercicio4.png", "respuesta": 9}
    ]
    
    # Filtrar solo los ejercicios disponibles
    ejercicios_respuestas = [er for er in ejercicios_respuestas if os.path.join(ruta_directorio, er["imagen"]) in ejercicios]

    # Barajar los ejercicios para añadir aleatoriedad
    random.shuffle(ejercicios_respuestas)
    
    original_image = Image.open(os.path.join('ejercicios', 'tickverde.png'))
    resized_image = original_image.resize((100, 100), Image.Resampling.LANCZOS)
    button_image1 = ImageTk.PhotoImage(resized_image)
    btn_siguiente = tk.Button(root, text="CORRECTO", image=button_image1, command=lambda n="siguiente": button_click(n))
    btn_siguiente.place(x=50, y=50)

    original_image = Image.open(os.path.join('ejercicios', 'exit_man.png'))
    resized_image = original_image.resize((100, 100), Image.Resampling.LANCZOS)
    button_image2 = ImageTk.PhotoImage(resized_image)
    btn_detener = tk.Button(root, text="SALIR", image=button_image2, command=lambda n="salir": button_click(n))
    btn_detener.place(x=150, y=50)

    for n, ejercicio in enumerate(ejercicios_respuestas):
        # Mostrar el tutorial si es necesario
        load_and_show_image(os.path.join(ruta_directorio, ejercicio["imagen"]))
        speak("Encuentra la figura que es igual a la del circulo de entre todas estas.")
        acertado = False
        while not acertado:
            query = listen(tiempo_minimo=3, tiempo_maximo=3)
            
            if not query:
                continue
            
            if pattern_detener.search(query):
                btn_siguiente.destroy()
                btn_detener.destroy()
                return
            
            if pattern_siguiente.search(query):
                speak('Vale, pasemos al siguiente ejercicio.')
                break

            match = re.search(r"\b(\d+)\b", query)
            if not match:
                speak('Lo siento, no he escuchado bien el número.')
                continue
            
            respuesta_usuario = int(match.group(1))
            if respuesta_usuario == ejercicio["respuesta"]:
                if n == len(ejercicios_respuestas) - 1:
                    speak("¡Muy bien! Has acertado. Ya no quedan mas problemas.")
                else:
                    speak("Muy bien! Has acertado. A por el siguiente.")
                time.sleep(1)
                acertado = True
            else:
                speak("Me parece que es incorrecto.")
                time.sleep(1)
        
    btn_siguiente.destroy()
    btn_detener.destroy()
    
def juego_c():
    speak("Concentracion.")
    directorio = os.path.join('ejercicios', 'Concentracion')
    ruta_directorio = os.path.abspath(directorio)
    patrones = ['ejercicio1_*.png', 'ejercicio2_*.png', 'ejercicio3_*.png']
    mostrar_ocultar_botones(False)
    ejercicios_respuestas = {
        'ejercicio1_1.png': 6,
        'ejercicio1_2.png': 8,
        'ejercicio1_3.png': 10,
        'ejercicio2_1.png': 4,
        'ejercicio2_2.png': 6,
        'ejercicio2_3.png': 9,
        'ejercicio3_1.png': 7,
        'ejercicio3_2.png': 6,
        'ejercicio3_3.png': 4,
    }
    ejercicios = []
    for patron in patrones:
        imagenes = sorted(glob.glob(os.path.join(ruta_directorio, patron)))
        if imagenes:
            imagen_seleccionada = random.choice(imagenes)
            ejercicios.append(imagen_seleccionada)

    for n, ejercicio in enumerate(ejercicios):
        # Mostrar el tutorial si es necesario
        load_and_show_image(os.path.join(ruta_directorio, ejercicio))
        speak("Cuantas figuras iguales al de ejemplo hay?")
        acertado = False
        while not acertado:
            query = listen(tiempo_minimo=3, tiempo_maximo=3)
            
            if not query:
                print('Nada.')
                continue
            
            if pattern_detener.search(query):
                btn_siguiente.destroy()
                btn_detener.destroy()
                return

            if pattern_siguiente.search(query):
                speak('Vale, pasemos al siguiente ejercicio.')
                break
        
            match = re.search(r"\b(\d+)\b", query)
            if not match:
                speak('Lo siento, no he escuchado bien el numero.')
                continue
            
            respuesta_usuario = int(match.group(1))
            if respuesta_usuario == ejercicios_respuestas[os.path.basename(ejercicio)]:
                if n == len(ejercicios) - 1:
                    speak("Muy bien! has acertado. Ya no quedan mas problemas.")
                else:
                    speak("Muy bien! Has acertado. A por el siguiente.")
                time.sleep(1)
                acertado = True
            else:
                speak("Me parece que es incorrecto.")
                time.sleep(1)
    main_loop(True)

def visualizar():
    global cap, player, lblVideo
    if cap is not None:
        ret, frame = cap.read()
        if ret == True:
            frame = cv2.resize(frame, (root.winfo_width(), root.winfo_height()))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            im = Image.fromarray(frame)
            img = ImageTk.PhotoImage(image=im)
            lblVideo.configure(image=img)
            lblVideo.image = img
            lblVideo.after(1, visualizar)
        else:
            liberar_recursos()
    else:
        liberar_recursos()

def remember():
    print(capturandoRostros.most_detected_unknown)
    # Aquí puedes decidir qué video reproducir basado en most_detected_unknown
    if (capturandoRostros.most_detected_unknown == 'Desconocido_3'):
        video_name = "prueba.mp4"
    else:
        video_name = "rick.mp4"
        
    try:
        script_dir = os.path.dirname(os.path.abspath(_file_))
    except NameError:
        script_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    video_path = os.path.join(script_dir, video_name)
    
    global lblVideo
    lblVideo = tk.Label(root)
    lblVideo.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0, anchor="nw")
    
    global cap, player
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        speak("No se pudo abrir la ventana")
    else:
        speak("El video se va a visualizar")
        player = MediaPlayer(video_path)
        lblVideo.lift() 
        visualizar()
       
def liberar_recursos():
    global cap, player, lblVideo
    if cap:
        cap.release()
    if player:
        player.close_player()
    if lblVideo:
        lblVideo.destroy()
    cap = None
    player = None
    lblVideo = None
    
def ayuda():
    load_and_show_image(os.path.join('init', "ayuda.png"))
    label_info.configure(fg='black')
    mensaje = """
    ¡Bienvenido al asistente de voz!
    
    Puedes usar los siguientes comandos:
    
    - Saludos: Puedes saludarme diciendo "Hola", "Buenos días", "Buenas tardes" o "Buenas noches".
    
    - Consultar la hora: Simplemente menciona "hora" y te diré la hora actual.
    
    - Consultar eventos: Di "consultar eventos" para ver los eventos agendados para hoy.
    
    - Agregar evento: Di "agregar evento" para añadir un nuevo evento a tu agenda.
    
    - Modificar evento: Si necesitas hacer cambios de horario a un evento existente, di "modificar evento".
    
    - Eliminar evento: Di "eliminar evento" para borrar un evento de tu agenda.
    
    - Mostrar tareas: Para ver tus tareas pendientes, di "mostrar tareas".
    
    - Agregar tarea: Para añadir una nueva tarea a tu lista, di "agregar tarea".
    
    - Marcar tarea como completada: Si has completado una tarea, di "marcar tarea como completada".
    
    - Eliminar tarea: Si deseas borrar una tarea de tu lista, di "eliminar tarea".
    
    - Agregar nota: Puedes guardar notas de voz diciendo "agregar nota".
    
    - Reproducir nota: Si quieres escuchar tus notas guardadas, di "reproducir nota".
    
    - Eliminar nota: Para eliminar una nota, simplemente di "eliminar nota".
    
    - Configurar alarma: Si necesitas una alarma, di "alarma".
    
    - Configurar temporizador: Para establecer un temporizador, di "temporizador".
    
    - Configurar contador: Para establecer un contador, di "cuenta"
    
    - Juegos: ¡También puedo entretenerte con algunos juegos!
    
    - Ayuda: Siempre puedes pedir ayuda diciendo "ayuda" o "ayúdame por favor".
    
    ¡Espero que encuentres útiles estas opciones!
    """
    print(mensaje)
    label_info.config(text=mensaje)
    ajustar_tamaño_texto()
    speak(mensaje)

# Función para escuchar al usuario y manejar errores de escucha

# Define la ruta al modelo de reconocimiento de voz
model_path = "/home/jacot/Downloads/RLP-2324-1631153-patch-4/Lopako/vosk-model-small-es-0.42"

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

def listen(tiempo_minimo=2, tiempo_maximo=4):
    global activacion
    
    try:
        eliminar = False
        if activacion:
            # Dibujar la franja azul que ocupe todo el ancho
            franja = canvas.create_rectangle(0, 0, root.winfo_screenwidth(), 30, outline="")
            canvas.itemconfig(franja, fill="cyan")
            eliminar = True
        
        print("Escuchando...")
        start_time_maximo = time.time()
        start_time_minimo = time.time()  # Almacena el tiempo sin escuchar nada
        audio_buffer = []  # Almacena el audio durante el tiempo de escucha
        
        while time.time() - start_time_maximo < tiempo_maximo:
            #print(time.time() - start_time_maximo, "<", tiempo_maximo)
            data = stream.read(CHUNK)
            
            if recognizer.AcceptWaveform(data):
                audio_buffer.append(data)  # Agrega el audio al buffer
        
            audio_array = np.frombuffer(data, dtype=np.int16)
            energia_promedio = np.mean(np.abs(audio_array))
        
            if energia_promedio > 750:
                start_time_minimo = time.time()
                #print("Tiempo mínimo reiniciado")
            else:
                #print(time.time() - start_time_minimo, ">=", tiempo_minimo)
                if time.time() - start_time_minimo >= tiempo_minimo:
                    #print("Tiempo mínimo sin hablar superado")
                    break
                
        if eliminar:
            canvas.delete(franja)  # Eliminar la franja azul del lienzo
            
        # Procesa el audio acumulado para obtener el texto escuchado
        recognizer.AcceptWaveform(b''.join(audio_buffer))
        result = recognizer.Result()
        query = eval(result)["text"]
        if query is not None:
            query = convertir_numeros(query).lower()
            print(f"¿Has dicho: {query}?")
            return query
            
        return ""
    except Exception as e:  # Maneja cualquier excepción
        print("Error:", e)
        return ""

def convertir_numeros(texto):
    palabras = texto.split()  # Divide el texto en palabras
    
    # Primer bucle: convierte palabras a números si es posible
    i = 0
    while i < len(palabras):
        try:
            palabra = palabras[i] # Toma la palabra actual
            if not palabra.isdigit(): # Verifica si la palabra no es un número
            
                if palabra == "un":
                    palabra = "uno"
                    
                numero = w2n.word_to_num(palabra) # Convierte la palabra a número
            else:
                numero = int(palabra) # Si ya es un número, conviértelo a entero
            #print(type(numero))
            
            if numero == 1000000000: # Si es mil millones, conviértelo a un millón
                numero = 1000000
                
            if isinstance(numero, int): # Si es un entero, reemplaza la palabra por el número
                palabras[i] = str(numero)
                #print(palabra, "=", numero)
        except ValueError: 
            # Maneja errores de conversión
            pass
        
        i += 1
    
    # Segundo bucle: procesa la suma y la multiplicación
    i = 1
    while i < len(palabras):
        
        # Si hay una palabra "y" entre dos números
        if i + 2 < len(palabras) and palabras[i + 1] == "y":
            try:
                numero_1 = palabras[i + 0]
                if numero_1.isdigit():
                    numero_1 = int(numero_1)
                #print(type(numero_1))
                
                numero_2 = palabras[i + 2]
                if numero_2.isdigit():
                    numero_2 = int(numero_2)
                #print(type(numero_2))
                
                # Si ambos son enteros, realiza la suma
                if isinstance(numero_1, int) and isinstance(numero_2, int):
                    palabras[i + 0:i + 3] = [str(numero_1 + numero_2)]
                    #print(numero_1, "+y", numero_2, "=", palabras[i])
            except (ValueError, IndexError):
                pass
            
        try:
            numero_1 = palabras[i - 1]
            if numero_1.isdigit():
                numero_1 = int(numero_1)
            #print(type(numero_1))
            
            numero_2 = palabras[i + 0]
            if numero_2.isdigit():
                numero_2 = int(numero_2)
            #print(type(numero_2))

            # Si ambos son enteros, procesa la operación
            if isinstance(numero_1, int) and isinstance(numero_2, int):
                if numero_2 == 1000 or numero_2 == 1000000:
                    palabras[i - 1:i + 1] = [str(numero_1 * numero_2)]
                    #print(numero_1, "*", numero_2, "=", palabras[i - 1])
                    continue
                else:
                    if numero_1 == 100:
                        palabras[i - 1:i + 1] = [str(numero_1 + numero_2)]
                        #print(numero_1, "+", numero_2, "=", palabras[i - 1])
                        continue
                    
                    if i + 1 < len(palabras):
                        numero_3 = palabras[i + 1]
                        if numero_3.isdigit():
                            numero_3 = int(numero_3)
                        #print(type(numero_3))
    
                        if isinstance(numero_2, int) and isinstance(numero_3, int):
                            if numero_3 == 1000:
                                palabras[i + 0:i + 2] = [str(numero_2 * numero_3)]
                                #print(numero_2, "*", numero_3, "=", palabras[i + 0])
                                continue
                    
                    palabras[i - 1:i + 1] = [str(numero_1 + numero_2)]
                    #print(numero_1, "+", numero_2, "=", palabras[i - 1])
                    continue
        except (ValueError, IndexError):
            pass
        
        i += 1
    return ' '.join(palabras) # Une las palabras en un texto nuevamente

def inicializar_botones(root):
    global btn_jugar, btn_preguntas, btn_recuerda
    btn_jugar = tk.Button(root, text="Jugar", relief="flat", bd=0)
    btn_preguntas = tk.Button(root, text="Preguntas", relief="flat", bd=0)
    btn_recuerda = tk.Button(root, text="Recuerda", relief="flat", bd=0)

def mostrar_botones():
    global btn_jugar, btn_preguntas, btn_recuerda
    estilo_botones = {
            "font": ("Helvetica", 32, "bold"),  
            "bg": "#B39DDB",  
            "fg": "white",  
            "borderwidth": 2, 
            "relief": "raised" 
    }
    btn_jugar.config(**estilo_botones)
    btn_preguntas.config(**estilo_botones)
    btn_recuerda.config(**estilo_botones)
    btn_jugar.place(x=90, y=450, width=250, height=100)
    btn_preguntas.place(x=390, y=250, width=250, height=100)
    btn_recuerda.place(x=700, y=450, width=250, height=100)

def ocultar_botones():

    btn_jugar.place_forget()
    btn_preguntas.place_forget()
    btn_recuerda.place_forget()

def mostrar_ocultar_botones(mostrar):
        if mostrar:
            mostrar_botones()
        else:
            ocultar_botones()

pattern_activacion = re.compile(r"\b(paco|opaco|pago|bajo|macho|banco)\b", re.IGNORECASE)

def main_loop(inicioauto = False):
    global activacion_flag
    global screen_width, screen_height 
    if (inicioauto):
        activacion_flag = True
    global alarma_activada
    alarma_activada = False
    

    global detener
    detener = False
    
    global terapia
    terapia = False
    
    global ayuda_var
    ayuda_var = False

    def cambiar_imagen_fondo():
        if not terapia and not ayuda_var:
            imagenes = [f for f in os.listdir('init/asistente') if f.endswith(('png', 'jpg', 'jpeg'))]
            ruta_directorio = os.path.join(os.getcwd(), directorio)
            imagen_aleatoria = random.choice(ruta_directorio)
            load_and_show_image(os.path.join('init/asistente', imagen_aleatoria))
            root.after(5000, cambiar_imagen_fondo)  # Llama de nuevo a la función después de 5 segundos
    if not activacion_flag:
        directorio = os.path.join('init', "black_logo.png")
        ruta_directorio = os.path.join(os.getcwd(), directorio)
        load_and_show_image(ruta_directorio)
        time.sleep(2)
        load_and_show_image(os.path.join(os.getcwd(), os.path.join('init', "INICIO.png")))
        speak("Hola soy Lopako, tu nuevo amigo.")
        load_and_show_image(os.path.join(os.getcwd(), os.path.join('init', "INICIO2.png")))
        speak("Por favor, mira a camara un momento.")
        time.sleep(3)
        load_and_show_image(os.path.join(os.getcwd(), os.path.join('init', "asistente.png")))
        label_info.config(text="Lopako")
        ajustar_tamaño_texto()
        btn_menu = tk.Button(root, text="LOPAKO", font= ("Helvetica", 48, "bold"), fg= "white", command=activacion, bg="black", relief="flat", bd=0)
        btn_menu.place(x=362, y=250, width=300, height=100)
        root.after(5000, cambiar_imagen_fondo)
    while not detener:
        if not alarma_activada:
            if activacion_flag:
                    label_info.config(text="")
                    ajustar_tamaño_texto()
                    #speak("Hola, que quieres hacer hoy")
                    moverservo()
                    load_and_show_image(os.path.join(os.getcwd(), os.path.join('init', "menu.png")))
                    if(btn_menu):
                        btn_menu.place_forget()
                    if(btn_pregunta_siguiente):
                        btn_pregunta_siguiente.place_forget()
                    terapia = True
                    mostrar_ocultar_botones(True)
                    activacion_flag = False
            query = listen(tiempo_minimo=2, tiempo_maximo=4)
            if query:                  
                if pattern_juegos.search(query):
                    mostrar_ocultar_botones(False)
                    ejecutar_juego_aleatorio()
                    
                    
                elif pattern_back.search(query):
                    mostrar_ocultar_botones(False)
                    load_and_show_image(os.path.join(os.getcwd(), os.path.join('init', "menu.png")))
                    btn_menu.place_forget()

                elif pattern_remember.search(query):
                    mostrar_ocultar_botones(False)
                    remember()
                    

                # Despedida
                elif pattern_despedida.search(query):
                    speak("¡Hasta luego! Que tengas un buen día.")
                # Ayuda
                elif pattern_ayuda.search(query):
                    ayuda_var = True
                    ayuda()
                    ayuda_var = False
                    load_and_show_image(os.path.join(os.getcwd(), os.path.join('init', "asistente.png")))
                    speak("¿En qué puedo ayudarte?")
                    continue
                elif pattern_activacion.search(query):
                    activacion_flag = True
                # Procesamiento de consultas generales
                elif pattern_saludo.search(query):
                    speak("Hola, en que puedo ayudarte?")
                    continue
                
                # Configuracion del sistema
                elif pattern_cambiar_color.search(query):
                    cambiar_color(query)
                else:
                    continue
                activacion_flag = False
                if(terapia == False): 
                    label_info.config(text="Lopako") 
                else: label_info.config(text="")
                ajustar_tamaño_texto()


def detener_programa():
    global detener
    detener = True
    
    root.quit()  # Detener el bucle principal de Tkinter
    root.destroy()  # Cierra la ventana principal
    if main_thread and main_thread.is_alive():
        main_thread.join()  # Espera a que el hilo principal termine antes de salir
    sys.exit()  # Sale del programa por completo

def ajustar_tamaño_texto(event=None):
    texto = label_info["text"]
    lineas = texto.split("\n")
    longitud_maxima = max(len(linea) for linea in lineas)
    altura_maxima = len(lineas)
    
    # Buscamos el tamaño de fuente más cercano para la longitud máxima de la línea
    tamaño_fuente_ancho = None
    for tamaño, longitud in sorted(letras_por_linea.items(), reverse=True):
        if longitud >= longitud_maxima:
            tamaño_fuente_ancho = tamaño
            break
    if tamaño_fuente_ancho is None:
        tamaño_fuente_ancho = 10  # Si no se encontró ninguna coincidencia, asignamos un valor por defecto
    
    # Buscamos el tamaño de fuente más cercano para la altura máxima de texto
    tamaño_fuente_alto = None
    for tamaño, altura in sorted(lineas_por_pantalla.items(), reverse=True):
        if altura >= altura_maxima:
            tamaño_fuente_alto = tamaño
            break
    if tamaño_fuente_alto is None:
        tamaño_fuente_alto = 10  # Si no se encontró ninguna coincidencia, asignamos un valor por defecto
    
    # Obtenemos el tamaño de fuente más pequeño para asegurarnos de que quepa tanto por ancho como por alto
    tamaño_fuente = min(tamaño_fuente_ancho, tamaño_fuente_alto)
    
    # Reducir el tamaño del texto
    tamaño_fuente = max(tamaño_fuente // 2, 10)
    
    label_info.config(font=("Arial", tamaño_fuente))
    label_info.update()
    
def calcular_letras_por_linea(ventana):
    tamaño_fuente_por_linea = {}
    for tamaño_fuente in range(10, 101):  # Tamaños de fuente de 10 a 50
        font = Font(size=tamaño_fuente)
        ancho_caracter = font.measure("W")  # Anchura de un carácter genérico
        ancho_ventana = ventana.winfo_screenwidth() * 2
        tamaño_fuente_por_linea[tamaño_fuente] = int(ancho_ventana // ancho_caracter)
    return tamaño_fuente_por_linea

def activacion():
    global activacion_flag
    activacion_flag = True
    print("activacion_flag cambiado a True") 

def calcular_lineas_por_pantalla(ventana):
    lineas_por_pantalla = {}
    for tamaño_fuente in range(10, 101):  # Tamaños de fuente de 10 a 50
        font = Font(size=tamaño_fuente)
        altura_linea = font.metrics("linespace") * 2
        altura_pantalla = ventana.winfo_screenheight()
        lineas_por_pantalla[tamaño_fuente] = int(altura_pantalla // altura_linea)
    return lineas_por_pantalla
    

# Esta función carga y muestra una imagen en un widget Label de Tkinter
def load_and_show_image(image_path):
    if image_path:
        # Obtener las dimensiones de la pantalla
        screen_width = label_info.winfo_screenwidth()
        screen_height = label_info.winfo_screenheight()
    
        # Cargar la imagen y redimensionarla para que ocupe toda la pantalla
        image = Image.open(image_path)
        image = image.resize((screen_width, screen_height))
        
        # Convertir la imagen para mostrarla en Tkinter
        photo = ImageTk.PhotoImage(image)
    
        # Configurar la imagen en el widget Label
        label_info.configure(image=photo)
        label_info.image = photo  # Mantén una referencia global a la imagen
        label_info.update()
    else:
        # Configurar la imagen en el widget Label
        label_info.configure(image="")
        label_info.update()

# Esta función carga y reproduce el audio correspondiente a la dirección dada
def load_and_play_audio(audio_path):
    playsound(audio_path)

def show_image(image):
    with canvas(device) as draw:
        draw.bitmap((0, 0), image, fill="white")
def run_script(script_path):
    # Ejecutar el script externo
    subprocess.run(["python", script_path])
    
def ojos():
    eye_open = Image.open('eyeopen.png').convert('1').resize((screen_width, screen_height)).transpose(Image.FLIP_TOP_BOTTOM)
    eye_closed = Image.open('eyeclosed.png').convert('1').resize((screen_width, screen_height)).transpose(Image.FLIP_LEFT_RIGHT)
    
    while True:
        show_image(eye_open)
        
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

# Crear la ventana principal
root = tk.Tk()
root.title("Lopako")

# Ajustar tamaño de la ventana para que ocupe toda la pantalla
root.attributes('-fullscreen', True)

# Crear el widget Label con texto
label_info = tk.Label(root, text="", justify="center", compound="center")
label_info.pack(expand=True, fill='both')
label_info.configure(fg="white")

letras_por_linea = calcular_letras_por_linea(label_info)
lineas_por_pantalla = calcular_lineas_por_pantalla(label_info)

# Crear un lienzo (canvas) y hacer que ocupe todo el ancho
canvas = tk.Canvas(root, height=30)
canvas.pack(side="bottom", fill="x")

# Cargar la imagen
# image = Image.open("prueba.png")
# photo = ImageTk.PhotoImage(image)

# Obtener las dimensiones de la imagen
# width, height = image.size


btn_jugar = tk.Button(root, text="Jugar", command = ejecutar_juego_aleatorio)
btn_preguntas = tk.Button(root, text="Preguntas", command = preguntas)
btn_recuerda = tk.Button(root, text="Recuerda", command = remember)
btn_pregunta_siguiente = tk.Button(root, text="Siguiente", command=preguntas)

#comenzar el bucle principal en un hilo aparte
rostros_thread = threading.Thread(target=start_capturing)
main_thread = threading.Thread(target=main_loop)
eyes_thread = threading.Thread(target=run_script, args=("OJOS.py",))

rostros_thread.start()
main_thread.start()
eyes_thread.start()

indice_pregunta = 0
# Ejecutar la aplicación
root.mainloop()
