import vosk
import pyaudio
import time
import numpy as np
from word2number_es import w2n

def convertir_numeros(texto):
    palabras = texto.split()  # Divide el texto en palabras
    
    # Primer bucle: convierte palabras a números si es posible
    i = 0
    while i < len(palabras):
        try:
            palabra = palabras[i] # Toma la palabra actual
            if not palabra.isdigit(): # Verifica si la palabra no es un número
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
                    
                    if i + 1 < len(palabras):
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

def listen(tiempo_minimo=3, tiempo_maximo=10):
    try:
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
                print("Tiempo mínimo reiniciado")
            else:
                #print(time.time() - start_time_minimo, ">=", tiempo_minimo)
                if time.time() - start_time_minimo >= tiempo_minimo:
                    #print("Tiempo mínimo sin hablar superado")
                    break
        
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


print("Habla ahora...")

# Procesa el audio en tiempo real
while True:
    listen()