import vosk
import pyaudio
import pyttsx3
import re
import os
import threading
import time
import numpy as np
from word2number_es import w2n
import tkinter as tk
from tkinter.font import Font
from tkinter import ttk
from playsound import playsound  
from PIL import Image, ImageTk  
import glob
import random
import cv2
import imutils
from capturandoRostros import capturando_rostros

def start_capturing():
    capturando_rostros()
    
rostros_thread = threading.Thread(target=start_capturing)
rostros_thread.start()

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

# Juegos y terapias
pattern_juegos = re.compile(r"\b(jugar)\b", re.IGNORECASE)
pattern_remember = re.compile(r"\b(recordar)\b", re.IGNORECASE)
pattern_preguntar = re.compile(r"\b(preguntar)\b", re.IGNORECASE)

pattern_af = re.compile(r"\b(atención|focal|atención focal)\b", re.IGNORECASE)
pattern_bv = re.compile(r"\b(busqueda|visual|busqueda visual)\b", re.IGNORECASE)
pattern_c = re.compile(r"\b(concentración)\b", re.IGNORECASE)

# Otros
pattern_detener = re.compile(r"\b(para|basta|detente|termina|atras|retroceder|atrás|salir)\b", re.IGNORECASE)

def terapia():
    global activacion
    label_info.config(text="")
    while True:
        load_and_show_image(os.path.join('init', "menu.png"))
        
        show_buttons([{'name':'Jugar','code':'jugar'}, {'name':'Preguntar','code':'preguntar'},
                      {'name':'Recordar','code':'recordar'}, {'name':'Atrás','code':'atras'}])
        
        speak('Puedes decir jugar para elegir jugar o recordar para elegir recordar, sino di atras para salir.')
        
        terapia = None
        while not terapia:
            text = 'Puedes decir "jugar" para elegir jugar o "recordar" para elegir recordar, sino di "atras" para salir'
            terapia_str = listen(advice_text=text)
            if pattern_detener.search(terapia_str):
                hide_buttons()
                return
            terapia = parsear_terapia(terapia_str)
            
            if terapia_str and not terapia:
                speak('Lo siento, no te he entendido.')
        
        hide_buttons()
        if terapia == 1:
            juego()
        elif terapia == 2:
            remember()
        elif terapia == 3:
            preguntar()

def parsear_terapia(terapia):
    if pattern_juegos.search(terapia):
        return 1   
    elif pattern_remember.search(terapia):
        return 2
    elif pattern_preguntar.search(terapia):
        return 3
    else:
        return None

def juego():
    while True:
        load_and_show_image(os.path.join('ejercicios', "menu_juegos.png")) 
        
        show_buttons([{'name':'Atención Focal','code':'atención'}, {'name':'Búsqueda Visual','code':'busqueda'},
                      {'name':'Concentración','code':'concentración'}, {'name':'Atrás','code':'atras'}])
        
        speak("Por favor, escoge una modalidad entre atención focal, búsqueda visual y concentración.")
        
        juego = None
        while not juego:
            text = 'Puedes decir "atencion", "busqueda" o "concentracion" para elegir el modo'
            juego_str = listen(advice_text=text)
            if pattern_detener.search(juego_str):
                hide_buttons()
                return
            juego = parsear_juego(juego_str)
            
            if juego_str and not juego:
                speak('Lo siento, no te he entendido.')
        
        hide_buttons()
        if juego == 1:
            juego_af()
        elif juego == 2:
            juego_bv()
        elif juego == 3:
            juego_c()
        
def parsear_juego(juego):
    if pattern_af.search(juego):
        return 1
    elif pattern_bv.search(juego):
        return 2
    elif pattern_c.search(juego):
        return 3
    else:
        return None

def juego_af():
    speak("Atención focal.")
    directorio = os.path.join('ejercicios', 'Atencion_focal')
    ruta_directorio = os.path.abspath(directorio)
    patrones = ['*.png']
    ejercicios = []
    for patron in patrones:
        ejercicios.extend(glob.glob(os.path.join(ruta_directorio, patron)))   

    # Pares de imágenes y respuestas correctas (asegúrate de que estén en el mismo orden)
    # Formato: {"imagen": "ruta_imagen", "respuesta": respuesta_correcta}
    ejercicios_respuestas = [
        {"imagen": "ejercicio1.png", "respuesta": 4},
        {"imagen": "ejercicio2.png", "respuesta": 4},
        {"imagen": "ejercicio3.png", "respuesta": 2},
        {"imagen": "ejercicio4.png", "respuesta": 3}
    ]
    
    # Filtrar solo los ejercicios disponibles
    ejercicios_respuestas = [er for er in ejercicios_respuestas if os.path.join(ruta_directorio, er["imagen"]) in ejercicios]
    
    # Barajar los ejercicios para añadir aleatoriedad
    random.shuffle(ejercicios_respuestas)

    for n, ejercicio in enumerate(ejercicios_respuestas):
        # Mostrar el tutorial si es necesario
        load_and_show_image(os.path.join(ruta_directorio, ejercicio["imagen"]))
        speak("De las imágenes de la derecha, ¿cuál es igual a la mostrada?")
        acertado = False
        while not acertado:
            query = listen(tiempo_minimo=3, tiempo_maximo=3)
            
            if not query:
                continue
            
            if pattern_detener.search(query):
                return

            match = re.search(r"\b(\d+)\b", query)
            if not match:
                speak('Lo siento, no he escuchado bien el número.')
                continue
            
            respuesta_usuario = int(match.group(1))
            if respuesta_usuario == ejercicio["respuesta"]:
                if n == len(ejercicios_respuestas) - 1:
                    speak("¡Muy bien! Has acertado. Ya no quedan más problemas.")
                else:
                    speak("¡Muy bien! Has acertado. A por el siguiente.")
                time.sleep(1)
                acertado = True
            else:
                speak("Me parece que es incorrecto.")
                time.sleep(1)
             
    
def juego_bv():
    speak("Búsqueda visual.")
    directorio = os.path.join('ejercicios', 'Busqueda_visual')
    ruta_directorio = os.path.abspath(directorio)
    patrones = ['*.png']
    ejercicios = []
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

    for n, ejercicio in enumerate(ejercicios_respuestas):
        # Mostrar el tutorial si es necesario
        load_and_show_image(os.path.join(ruta_directorio, ejercicio["imagen"]))
        speak("Encuentra la figura que es igual a la del círculo de entre todas estas.")
        acertado = False
        while not acertado:
            query = listen(tiempo_minimo=3, tiempo_maximo=3)
            
            if not query:
                continue
            
            if pattern_detener.search(query):
                return

            match = re.search(r"\b(\d+)\b", query)
            if not match:
                speak('Lo siento, no he escuchado bien el número.')
                continue
            
            respuesta_usuario = int(match.group(1))
            if respuesta_usuario == ejercicio["respuesta"]:
                if n == len(ejercicios_respuestas) - 1:
                    speak("¡Muy bien! Has acertado. Ya no quedan más problemas.")
                else:
                    speak("¡Muy bien! Has acertado. A por el siguiente.")
                time.sleep(1)
                acertado = True
            else:
                speak("Me parece que es incorrecto.")
                time.sleep(1)

def juego_c():
    speak("Concentracion.")
    directorio = os.path.join('ejercicios', 'Concentracion')
    ruta_directorio = os.path.abspath(directorio)
    patrones = ['*.png']
    ejercicios = []
    for patron in patrones:
        ejercicios.extend(glob.glob(os.path.join(ruta_directorio, patron)))

    # Pares de imágenes y respuestas correctas (asegúrate de que estén en el mismo orden)
    # Formato: {"imagen": "ruta_imagen", "respuesta": respuesta_correcta}
    ejercicios_respuestas = [
        {"imagen": 'ejercicio1_1.png', "respuesta": 6},
        {"imagen": 'ejercicio1_2.png', "respuesta": 8},
        {"imagen": 'ejercicio1_3.png', "respuesta": 10},
        {"imagen": 'ejercicio2_1.png', "respuesta": 4},
        {"imagen": 'ejercicio2_2.png', "respuesta": 6},
        {"imagen": 'ejercicio2_3.png', "respuesta": 9},
        {"imagen": 'ejercicio3_1.png', "respuesta": 7},
        {"imagen": 'ejercicio3_2.png', "respuesta": 6},
        {"imagen": 'ejercicio3_3.png', "respuesta": 4}
    ]
    
    # Filtrar solo los ejercicios disponibles
    ejercicios_respuestas = [er for er in ejercicios_respuestas if os.path.join(ruta_directorio, er["imagen"]) in ejercicios]

    # Barajar los ejercicios para añadir aleatoriedad
    random.shuffle(ejercicios_respuestas)

    for n, ejercicio in enumerate(ejercicios_respuestas):
        # Mostrar el tutorial si es necesario
        load_and_show_image(os.path.join(ruta_directorio, ejercicio["imagen"]))
        speak("¿Cuantas figuras iguales al de ejemplo hay?")
        acertado = False
        while not acertado:
            query = listen(tiempo_minimo=3, tiempo_maximo=3)
            
            if not query:
                continue
            
            if pattern_detener.search(query):
                return

            match = re.search(r"\b(\d+)\b", query)
            if not match:
                speak('Lo siento, no he escuchado bien el número.')
                continue
            
            respuesta_usuario = int(match.group(1))
            if respuesta_usuario == ejercicio["respuesta"]:
                if n == len(ejercicios_respuestas) - 1:
                    speak("¡Muy bien! Has acertado. Ya no quedan más problemas.")
                else:
                    speak("¡Muy bien! Has acertado. A por el siguiente.")
                time.sleep(1)
                acertado = True
            else:
                speak("Me parece que es incorrecto.")
                time.sleep(1)

def visualizar():
    global cap
    global lblVideo
    if cap is not None:
        ret, frame = cap.read()
        if ret == True:
            frame = imutils.resize(frame, width=640)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            im = Image.fromarray(frame)
            img = ImageTk.PhotoImage(image=im)
            lblVideo.configure(image=img)
            lblVideo.image = img
            lblVideo.after(10, visualizar)
        else:
            lblVideo.image = ""
            cap.release()

def remember():
    # Construir la ruta relativa al directorio del script actual
    script_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(script_dir, "remembere.mp4")
    
    global lblVideo
    lblVideo = tk.Label(root)
    lblVideo.pack(expand=True, fill='both')
    
    global cap
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        speak("No se pudo abrir la ventana")
    else:
        speak("El video se va a visualizar")
        lblVideo.lift()
        visualizar()
    
    lblVideo.destroy()

def preguntar():
    # Función placeholder para la nueva modalidad de preguntar
    speak("La modalidad de preguntar aún no está implementada.")
    # Aquí puedes agregar la lógica para la nueva modalidad cuando esté lista

# Función para escuchar al usuario y manejar errores de escucha

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

def listen(tiempo_minimo=3, tiempo_maximo=10, advice_text=None):
    global activacion
    global alarma_activada
    global skip
    
    try:
        eliminar = False
        if activacion:
            # Crear un lienzo (canvas) y hacer que ocupe todo el ancho
            canvas = tk.Canvas(label_info, height=30)
            canvas.pack(side="bottom", fill="x")
            
            # Dibujar la franja azul que ocupe todo el ancho
            franja = canvas.create_rectangle(0, 0, root.winfo_screenwidth(), 30, outline="")
            canvas.itemconfig(franja, fill="cyan")
            eliminar = True
            
        if advice_text:
            advice_label = tk.Label(root, text="", font=("Arial", 20), justify="center", anchor="center")
            advice_label.place(relx=0.05, rely=0.90)

            advice_label.config(text=advice_text)
            advice_label.update()
        
        print("Escuchando...")
        start_time_maximo = time.time()
        start_time_minimo = time.time()  # Almacena el tiempo sin escuchar nada
        audio_buffer = []  # Almacena el audio durante el tiempo de escucha
        
        while time.time() - start_time_maximo < tiempo_maximo and not skip:
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
            canvas.destroy()  # Eliminar la franja azul del lienzo
        
        if advice_text:
            advice_label.destroy()
            
        if skip:
            skip = False
            return resultado
        
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
    i = 0
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
            numero_1 = palabras[i + 0]
            if numero_1.isdigit():
                numero_1 = int(numero_1)
            #print(type(numero_1))
            
            numero_2 = palabras[i + 1]
            if numero_2.isdigit():
                numero_2 = int(numero_2)
            #print(type(numero_2))

            # Si ambos son enteros, procesa la operación
            if isinstance(numero_1, int) and isinstance(numero_2, int):
                if numero_2 == 1000 or numero_2 == 1000000:
                    palabras[i + 0:i + 2] = [str(numero_1 * numero_2)]
                    #print(numero_1, "*", numero_2, "=", palabras[i - 1])
                    continue
                else:
                    if numero_1 == 100:
                        palabras[i + 0:i + 2] = [str(numero_1 + numero_2)]
                        #print(numero_1, "+", numero_2, "=", palabras[i - 1])
                        continue
                    
                    if i + 2 < len(palabras):
                        numero_3 = palabras[i + 2]
                        if numero_3.isdigit():
                            numero_3 = int(numero_3)
                        #print(type(numero_3))
    
                        if isinstance(numero_2, int) and isinstance(numero_3, int):
                            if numero_3 == 1000:
                                palabras[i + 1:i + 3] = [str(numero_2 * numero_3)]
                                #print(numero_2, "*", numero_3, "=", palabras[i + 0])
                                continue
                    
                    palabras[i + 0:i + 2] = [str(numero_1 + numero_2)]
                    #print(numero_1, "+", numero_2, "=", palabras[i - 1])
                    continue
        except (ValueError, IndexError):
            pass
        
        i += 1
    return ' '.join(palabras) # Une las palabras en un texto nuevamente


pattern_activacion = re.compile(r"\b(paco|opaco|pago|bajo|macho|banco)\b", re.IGNORECASE)

def main_loop():
    global activacion
    activacion = False
    
    global detener
    detener = False
    
    # Carga la imagen inicial
    load_and_show_image(os.path.join('init', "black.png"))
    load_and_play_audio(os.path.join('audios', "encendido.mp3"))
    load_and_show_image(os.path.join('init', "black_logo.png"))
    time.sleep(2)
    load_and_show_image(os.path.join('init', "asistente.png"))
    label_info.config(text="Lopako")
    ajustar_tamaño_texto()
    show_buttons([{'name':'Activar','code':'paco'}])
    
    while not detener:
        if not activacion:   
            random_advice = random.choice(advice_list)
            query = listen(tiempo_minimo=3, tiempo_maximo=10, advice_text=random_advice)
        
        if activacion:       
            terapia()
            activacion = False
            load_and_show_image(os.path.join('init', "asistente.png"))
            label_info.config(text="Lopako")
            ajustar_tamaño_texto()
            show_buttons([{'name':'Activar','code':'paco'}])
            
        elif pattern_activacion.search(query):
            label_info.config(text="En qué puedo ayudarte?")
            ajustar_tamaño_texto()
            speak("¿En qué puedo ayudarte?")
            activacion = True

global resultado
global skip
skip = False

# Función para manejar el clic de los botones
def button_click(code):
    global resultado
    resultado = code
    
    global skip
    skip = True
    
    hide_buttons()  # Eliminar botones existentes

def show_buttons(button_info):
    hide_buttons()  # Eliminar botones existentes
    
    button_frame = tk.Frame(root)
    button_frame.place(relx=0.5, rely=0.75, anchor='center')

    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 12), padding=10, relief="flat", background="#4CAF50", foreground="black")
    style.map("TButton", background=[("active", "#45a049")])

    for i, info in enumerate(button_info):
        button = ttk.Button(button_frame, text=info["name"], command=lambda n=info["code"]: button_click(n), style="TButton")
        button.grid(row=0, column=i, padx=5, pady=5)

def hide_buttons():
    for widget in root.winfo_children():
        if isinstance(widget, tk.Frame):
            widget.destroy()

def ajustar_tamaño_texto(event=None):
    texto = label_info["text"]
    lineas = texto.split("\n")
    longitud_maxima = max(len(linea) for linea in lineas)
    altura_maxima = len(lineas)
    
    # Buscamos el tamaño de fuente más cercano para la longitud máxima de la línea
    tamaño_fuente_ancho = None
    for tamaño, longitud in sorted(letras_por_linea.items(), reverse=True):
        #print(longitud, ">=", longitud_maxima)
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
    
    label_info.config(font=("Arial", tamaño_fuente))
    label_info.update()
    
def calcular_letras_por_linea(ventana):
    tamaño_fuente_por_linea = {}
    for tamaño_fuente in range(10, 201):  # Tamaños de fuente de 10 a 50
        font = Font(size=tamaño_fuente)
        ancho_caracter = font.measure("W")  # Anchura de un carácter genérico
        ancho_ventana = ventana.winfo_screenwidth() * 1.5
        tamaño_fuente_por_linea[tamaño_fuente] = int(ancho_ventana // ancho_caracter)
    return tamaño_fuente_por_linea

def calcular_lineas_por_pantalla(ventana):
    lineas_por_pantalla = {}
    for tamaño_fuente in range(10, 201):  # Tamaños de fuente de 10 a 50
        font = Font(size=tamaño_fuente)
        altura_linea = font.metrics("linespace") * 1.5
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

# Crear la ventana principal
root = tk.Tk()
root.title("Lopako")

# Ajustar tamaño de la ventana para que ocupe toda la pantalla
root.attributes('-fullscreen', True)

# Maximiza la ventana para ocupar toda la pantalla
root.state('zoomed')

# Crear el widget Label con texto
label_info = tk.Label(root, text="", justify="center", compound="center", fg='white')
label_info.pack(expand=True, fill='both')

letras_por_linea = calcular_letras_por_linea(label_info)
lineas_por_pantalla = calcular_lineas_por_pantalla(label_info)

# Lista de consejos
advice_list = [
    'Terapia: ¡Puedo entretenerte con algunos juegos o hacerte recordar, solo di "terapia"!',
]

# Ejecutar el bucle principal en un hilo aparte
main_thread = threading.Thread(target=main_loop)
main_thread.start()

# Ejecutar la aplicación
root.mainloop()