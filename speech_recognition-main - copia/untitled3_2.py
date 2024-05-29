import vosk
import pyaudio
import pyttsx3
import re
import datetime
import calendar
import pickle
import threading
import time
import numpy as np
from word2number_es import w2n

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

# Eventos
pattern_consultar_eventos = re.compile(r"\b(ver|listar|consultar|revisar) ?(los)? (eventos)\b", re.IGNORECASE)
pattern_agregar_evento = re.compile(r"\b(agregar|crear|insertar|añadir|poner|añade|crea) ?(un ?(nuevo)?)? (evento)\b", re.IGNORECASE)
pattern_modificar_evento = re.compile(r"\b(modificar|editar|cambiar) ?(el|un)? (evento)\b", re.IGNORECASE)
pattern_eliminar_evento = re.compile(r"\b(eliminar|quitar|borrar) ?(el|un)? (evento)\b", re.IGNORECASE)

# Tareas
pattern_mostrar_tareas = re.compile(r"\b(ver|listar|consultar|revisar) ?(las)? (tareas)\b", re.IGNORECASE)
pattern_agregar_tarea = re.compile(r"\b(agregar|crear|insertar|añadir|poner|añade|crea) ?(una ?(nueva)?)? (tarea)\b", re.IGNORECASE)
pattern_marcar_completada = re.compile(r"\b(completar|marcar|checkear) ?(una|la)? (tarea)\b", re.IGNORECASE)
pattern_eliminar_tarea = re.compile(r"\b(eliminar|quitar|borrar) ?(una|la)? (tarea)\b", re.IGNORECASE)

# Notas
pattern_agregar_nota = re.compile(r"\b(agregar|crear|insertar|añadir|poner|añade|crea) ?(una ?(nueva)?)? (nota)\b", re.IGNORECASE)
pattern_reproducir_nota = re.compile(r"\b(ver|listar|consultar|revisar|reproducir|escuchar|oir) ?(una|la)? (nota)\b", re.IGNORECASE)
pattern_eliminar_nota = re.compile(r"\b(eliminar|quitar|borrar) ?(una|la)? (nota)\b", re.IGNORECASE)

# Reloj
pattern_consultar_hora = re.compile(r"\b(hora)\b", re.IGNORECASE)
pattern_configurar_alarma = re.compile(r"\b(alarma)\b", re.IGNORECASE)
pattern_configurar_temporizador = re.compile(r"\b(temporizador|temporizar)\b", re.IGNORECASE)
pattern_configurar_contador = re.compile(r"\b(contar|cuenta|contador)\b", re.IGNORECASE)

# Otros
pattern_juegos = re.compile(r"\b(juegos|jugar)\b", re.IGNORECASE)
pattern_ayuda = re.compile(r"\b(ayuda|ayúdame|instrucciones)\b", re.IGNORECASE)
pattern_saludo = re.compile(r"\b(hola|buenos días|buenas tardes|buenas noches)\b", re.IGNORECASE)
pattern_despedida = re.compile(r"\b(adiós|hasta luego|chao|nos vemos)\b", re.IGNORECASE)
pattern_detener = re.compile(r"\b(para|basta|detente|termina)\b", re.IGNORECASE)

def parsear_fecha(fecha_str):
    if not fecha_str:
        return None
    
    # Expresiones regulares para diferentes formatos de fecha
    formato_completo = r"(?P<dia>\d{1,2}) de (?P<mes>[a-zA-Z]+) de (?P<año>\d{4})"
    formato_dia_mes = r"el (?P<dia>\d{1,2}) de (?P<mes>[a-zA-Z]+)"
    formato_hoy = r"hoy"
    formato_manana = r"mañana"
    formato_dia_semana = r"(?P<dia_semana>lunes|martes|miércoles|jueves|viernes|sábado|domingo)"
    formato_dia = r"el (?P<dia>\d{1,2})"
    formato_pasado_manana = r"pasado mañana"

    # Mapeo de nombres de días y meses en inglés a español
    nombres_meses_ingles = list(calendar.month_name)[1:]
    nombres_meses_espanol = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    nombres_dias_ingles = list(calendar.day_name)
    nombres_dias_espanol = [
        "lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"
    ]

    # Convertir los nombres de días y meses en inglés a español
    for i, mes in enumerate(nombres_meses_ingles):
        fecha_str = fecha_str.replace(mes, nombres_meses_espanol[i])
    for i, dia in enumerate(nombres_dias_ingles):
        fecha_str = fecha_str.replace(dia, nombres_dias_espanol[i])

    # Buscar coincidencias para diferentes formatos de fecha
    match_completo = re.search(formato_completo, fecha_str, re.IGNORECASE)
    match_dia_mes = re.search(formato_dia_mes, fecha_str, re.IGNORECASE)
    match_hoy = re.search(formato_hoy, fecha_str, re.IGNORECASE)
    match_manana = re.search(formato_manana, fecha_str, re.IGNORECASE)
    match_dia_semana = re.search(formato_dia_semana, fecha_str, re.IGNORECASE)
    match_dia = re.search(formato_dia, fecha_str, re.IGNORECASE)
    match_pasado_manana = re.search(formato_pasado_manana, fecha_str, re.IGNORECASE)

    # Si se encuentra el formato completo (dia de mes de año)
    if match_completo:
        dia = int(match_completo.group('dia'))
        mes = match_completo.group('mes').capitalize()
        año = int(match_completo.group('año'))
        return datetime.datetime(year=año, month=mes, day=dia)

    # Si se encuentra el formato día y mes (el día de mes)
    elif match_dia_mes:
        dia = int(match_dia_mes.group('dia'))
        mes = match_dia_mes.group('mes').capitalize()
        año = datetime.datetime.now().year
        return datetime.datetime(year=año, month=mes, day=dia)

    # Si se encuentra la expresión "hoy"
    elif match_hoy:
        return datetime.datetime.now()

    # Si se encuentra la expresión "mañana"
    elif match_manana:
        return datetime.datetime.now() + datetime.timedelta(days=1)

    # Si se encuentra el día de la semana (el próximo día de la semana)
    elif match_dia_semana:
        dia_semana = match_dia_semana.group('dia_semana')
        hoy = datetime.datetime.now()
        dia_semana_num = nombres_dias_espanol.index(dia_semana.lower())
        delta_dias = (dia_semana_num - hoy.weekday() + 7) % 7
        if delta_dias == 0:
            delta_dias = 7
        fecha = hoy + datetime.timedelta(days=delta_dias)
        
        # Si la fecha encontrada es igual a la fecha actual, se avanza una semana
        if fecha.date() < datetime.datetime.now().date():
            fecha += datetime.timedelta(weeks=1)
        return fecha

    # Si se encuentra solo el día
    elif match_dia:
        dia = int(match_dia.group('dia'))
        mes_actual = datetime.datetime.now().month
        año_actual = datetime.datetime.now().year
        return datetime.datetime(year=año_actual, month=mes_actual, day=dia)

    # Si se encuentra la expresión "pasado mañana"
    elif match_pasado_manana:
        return datetime.datetime.now() + datetime.timedelta(days=2)

    else:
        return None

def parsear_hora(hora_str):
    if not hora_str:
        return None

    # Expresiones regulares para diferentes formatos de hora
    formato_simple = r"a\s*las?\s*(\d{1,2})(?::(\d{2}))?"
    formato_con_fraccion = r"a\s*las?\s*(\d{1,2})(?:\s*y\s*(un cuarto|media|tres cuartos|en punto))?"
    tiempo_futuro_regex = r"(?:en|dentro de)\s*(\d+)\s*(horas?|minutos?|segundos?)"

    # Expresiones literales para referencias a la mañana y a la tarde
    referencias_manana = ["mañana", "en la mañana", "por la mañana", "am"]
    referencias_tarde = ["tarde", "en la tarde", "por la tarde", "de la tarde", "pm"]

    # Buscar referencias literales a la mañana y a la tarde
    periodo = None
    for ref in referencias_manana:
        if ref in hora_str.lower():
            periodo = "a.m."
            break
    for ref in referencias_tarde:
        if ref in hora_str.lower():
            periodo = "p.m."
            break

    # Buscar coincidencias para diferentes formatos de hora
    match_simple = re.match(formato_simple, hora_str, re.IGNORECASE)
    match_con_fraccion = re.match(formato_con_fraccion, hora_str, re.IGNORECASE)
    match_futuro = re.search(tiempo_futuro_regex, hora_str, re.IGNORECASE)

    # Si se encuentra el formato simple (hora:minuto)
    if match_simple:
        hora = int(match_simple.group(1))
        minuto = int(match_simple.group(2)) if match_simple.group(2) else 0
        if 0 <= hora <= 12 and 0 <= minuto <= 59:
            if periodo and periodo.lower() == "p.m." and hora != 12:
                hora += 12
            return datetime.time(hour=hora, minute=minuto)

    # Si se encuentra el formato con fracción (cuarto, media, tres cuartos, punto)
    elif match_con_fraccion:
        hora = int(match_con_fraccion.group(1))
        fraccion = match_con_fraccion.group(2).lower()
        if 0 <= hora <= 12:
            if periodo and periodo.lower() == "p.m." and hora != 12:
                hora += 12
            if fraccion == "un cuarto":
                minuto = 15
            elif fraccion == "media":
                minuto = 30
            elif fraccion == "tres cuartos":
                minuto = 45
            elif fraccion == "en punto":
                minuto = 0
            return datetime.time(hour=hora, minute=minuto)

    # Si se encuentra una referencia a un tiempo futuro (horas, minutos, segundos)
    elif match_futuro:
        cantidad = int(match_futuro.group(1))
        unidad = match_futuro.group(2).lower()
        horas = 0
        minutos = 0
        segundos = 0
        if unidad.startswith('h'):  # Horas
            horas = cantidad
        elif unidad.startswith('m'):  # Minutos
            minutos = cantidad
        elif unidad.startswith('s'):  # Segundos
            segundos = cantidad
        # Calcular tiempo futuro
        tiempo_futuro = datetime.datetime.now() + datetime.timedelta(hours=horas, minutes=minutos, seconds=segundos)
        return tiempo_futuro.time()

    return None



# Funciones para gestionar la agenda y el calendario (offline)
def cargar_agenda():
    try:
        with open('agenda.pickle', 'rb') as archivo:
            agenda = pickle.load(archivo)
        return agenda
    except (FileNotFoundError, pickle.UnpicklingError):
        return {}

def guardar_agenda(agenda):
    with open('agenda.pickle', 'wb') as archivo:
        pickle.dump(agenda, archivo)

def consultar_eventos(agenda, query):
    if not agenda:
        speak("No hay eventos agendados.")
        return

    fecha = parsear_fecha(query)
    while not fecha:
        speak("¿Qué fecha deseas consultar? Puedes indicar el día, mes y/o año.")
        fecha_str = listen()
        if pattern_detener.search(fecha_str):
            return
        fecha = parsear_fecha(fecha_str)
        if not fecha:
            speak("No se detectó ninguna fecha. Por favor, intenta de nuevo.")
    
    eventos_hoy = []
    for fecha_agenda, eventos in agenda.items():
        if fecha_agenda.date() == fecha.date():
            for evento in eventos:
                eventos_hoy.append(f"{evento['hora']}: {evento['titulo']}")
    
    if not eventos_hoy:
        speak(f"No tienes eventos agendados para el {fecha.strftime('%d-%m-%Y')}. ¿Deseas consultar otro día?")
        respuesta = listen()
        if respuesta.lower() in ["sí", "si"]:
            consultar_eventos(agenda, "")
        else:
            return
    else:
        speak("Tus eventos son los siguientes:")
        for evento in eventos_hoy:
            speak(evento)
        return

def agregar_evento(agenda, query):
    fecha = parsear_fecha(query)
    while not fecha:
        speak("Por favor, indica la fecha del evento. Puedes especificar el día, mes y/o año.")
        fecha_str = listen()
        if pattern_detener.search(fecha_str):
            return
        fecha = parsear_fecha(fecha_str)
        if not fecha:
            speak("No se detectó ninguna fecha. Por favor, intenta de nuevo.")
    
    hora = parsear_hora(query)
    while not hora:
        speak("Por favor, indica la hora del evento.")
        hora_str = listen()
        if pattern_detener.search(hora_str):
            return
        hora = parsear_fecha(hora_str)
        if not fecha:
            speak("No se detectó ninguna hora. Por favor, intenta de nuevo.")
    
    titulo = None
    while not titulo:
        speak("Por favor, indica el título del evento.")
        titulo = listen(tiempo_minimo=5, tiempo_maximo=60)
        if pattern_detener.search(titulo):
            return
        if not titulo:
            speak("No se detectó ningún título. Por favor, intenta de nuevo.")    
    
    nuevo_evento = {'hora': hora.strftime('%H:%M'), 'titulo': titulo}
    fecha_str = fecha.strftime('%Y-%m-%d')
    if fecha_str not in agenda:
        agenda[fecha_str] = [nuevo_evento]
    else:
        agenda[fecha_str].append(nuevo_evento)
    guardar_agenda(agenda)
    speak(f"Evento agregado para el {fecha.strftime('%d-%m-%Y')} a las {hora.strftime('%H:%M')} con el título {titulo}.")


def modificar_evento(agenda, query):
    if not agenda:
        speak("No hay eventos agendados.")
        return
    
    fecha = parsear_fecha(query)
    while not fecha:
        speak("Por favor, indica la fecha del evento a modificar.")
        fecha_str = listen()
        if pattern_detener.search(fecha_str):
            return
        fecha = parsear_fecha(fecha_str)
        if not fecha:
            speak("No se detectó ninguna fecha. Por favor, intenta de nuevo.")
    
    fecha_str = fecha.strftime('%Y-%m-%d')
    if fecha_str not in agenda:
        speak(f"No hay eventos para el {fecha.strftime('%d-%m-%Y')}.")
        return
        
    speak(f"Eventos para el {fecha.strftime('%d-%m-%Y')}:")
    for evento in agenda[fecha_str]:
        speak(f"Hora: {evento['hora']}, Título: {evento['titulo']}")
    
    hora_vieja = None
    while not hora_vieja:
        speak("Por favor, indica la hora actual del evento.")
        hora_vieja_str = listen()
        if pattern_detener.search(hora_vieja_str):
            return
        hora_vieja = parsear_hora(hora_vieja_str)
        if not hora_vieja:
            speak("No se detectó ninguna hora actual. Por favor, intenta de nuevo.")

    hora_nueva = None
    while not hora_nueva:
        speak("Por favor, indica la nueva hora del evento.")
        hora_nueva_str = listen()
        if pattern_detener.search(hora_nueva_str):
            return
        hora_nueva = parsear_hora(hora_nueva_str)
        if not hora_nueva:
            speak("No se detectó ninguna hora nueva. Por favor, intenta de nuevo.")

    try:
        hora_vieja = hora_vieja.strftime('%H:%M')
        hora_nueva = hora_nueva.strftime('%H:%M')
    except ValueError:
        speak("Error: Formato de fecha u hora incorrecto.")
        return

    for i, evento in enumerate(agenda[fecha_str]):
        if evento['hora'] == hora_vieja:
            agenda[fecha_str][i] = {'hora': hora_nueva, 'titulo': evento['titulo']}
            guardar_agenda(agenda)
            speak(f"Evento modificado de las {hora_vieja} a las {hora_nueva}.")
            return

def eliminar_evento(agenda, query):
    if not agenda:
        speak("No hay eventos agendados.")
        return
    
    fecha = parsear_fecha(query)
    while not fecha:
        speak("Por favor, indica la fecha del evento a eliminar.")
        fecha_str = listen()
        if pattern_detener.search(fecha_str):
            return
        fecha = parsear_fecha(fecha_str)
        if not fecha:
            speak("No se detectó ninguna fecha. Por favor, intenta de nuevo.")

    fecha_str = fecha.strftime('%Y-%m-%d')
    if fecha_str not in agenda:
        speak(f"No hay eventos para el {fecha.strftime('%d-%m-%Y')}.")
        return

    hora = None
    while not hora:
        speak("Por favor, indica la hora del evento a eliminar.")
        hora_str = listen()
        if pattern_detener.search(hora_str):
            return
        hora = parsear_hora(hora_str)
        if not hora:
            speak("No se detectó ninguna hora. Por favor, intenta de nuevo.")

    try:
        hora_evento = hora.strftime('%H:%M')
    except ValueError:
        speak("Error: Formato de hora incorrecto.")
        return

    if not any(evento['hora'] == hora_evento for evento in agenda[fecha_str]):
        speak(f"No se encontró el evento para el {fecha.strftime('%d-%m-%Y')} a las {hora_evento}.")
        return

    for i, evento in enumerate(agenda[fecha_str]):
        if evento['hora'] == hora_evento:
            del agenda[fecha_str][i]
            if not agenda[fecha_str]:
                del agenda[fecha_str]
            guardar_agenda(agenda)
            speak(f"Evento eliminado para el {fecha.strftime('%d-%m-%Y')} a las {hora_evento}.")
            return


# Funciones para gestionar listas de tareas (offline)
def cargar_tareas():
    try:
        with open('tareas.pickle', 'rb') as archivo:
            tareas = pickle.load(archivo)
        return tareas
    except (FileNotFoundError, pickle.UnpicklingError):
        return {}

def guardar_tareas(tareas):
    with open('tareas.pickle', 'wb') as archivo:
        pickle.dump(tareas, archivo)

def mostrar_tareas(tareas):
    if not tareas:
        speak("No tienes tareas pendientes.")
        return
    
    speak("Tus tareas pendientes:")
    for i, tarea in enumerate(tareas):
        descripcion = tarea['descripcion']
        fecha_limite_str = tarea['fecha_limite'].strftime('%d-%m-%Y') if tarea['fecha_limite'] else "Sin fecha límite"
        estado = "Completada" if tarea.get('completada', False) else "Pendiente"
        speak(f"{i+1}. {descripcion}")
        speak(f"Fecha límite: {fecha_limite_str} - Estado: {estado}")

def agregar_tarea(tareas, query):

    descripcion = None
    while not descripcion:
        speak("Por favor, indica la descripción de la tarea.")
        descripcion_str = listen(tiempo_minimo=5, tiempo_maximo=60)
        if pattern_detener.search(descripcion_str):
            return
        descripcion = descripcion_str
        if not descripcion:
            speak("No se detectó ninguna descripción. Por favor, intenta de nuevo.")
    
    if re.compile(r"((sin|no ?(hay)?) ?(tiempo|fecha)? limite)", re.IGNORECASE).search(query):
        fecha_limite = "ninguna"
    else:
        fecha_limite = parsear_fecha(query)

    while not fecha_limite:
       speak("¿Hay una fecha límite para esta tarea? Indica la fecha en formato día-mes-año, o simplemente di no hay fecha límite.")
       fecha_limite_str = listen()
       if pattern_detener.search(fecha_limite_str):
           return

       if re.compile(r"((sin|no ?(hay)?) ?(tiempo|fecha)? limite)", re.IGNORECASE).search(fecha_limite_str):
           fecha_limite = "ninguna"
       else:
           fecha_limite = parsear_fecha(fecha_limite_str)
           
       if not fecha_limite:
           speak("No se detectó ninguna fecha límite. Por favor, intenta de nuevo.")     

    nueva_tarea = {'descripcion': descripcion, 'fecha_limite': fecha_limite, 'completada': False}
    tareas.append(nueva_tarea)
    guardar_tareas(tareas)
    speak(f"Tarea '{descripcion}' agregada.")

def marcar_tarea_como_completada(tareas, query):
    if not tareas:
        speak("No tienes tareas pendientes.")
        return
    
    numero_tarea = parsear_numero_elemento(query)
    while not numero_tarea:
        speak("Por favor, indica el número de la tarea que quieres marcar como completada.")
        numero_tarea_str = listen()
        if pattern_detener.search(numero_tarea_str):
            return
        numero_tarea = parsear_numero_elemento(numero_tarea_str)
        if not numero_tarea:
            speak("No se detectó ningún número de tarea. Por favor, intenta de nuevo.")
    
    try:
        numero_tarea = int(numero_tarea) - 1
        if 0 <= numero_tarea < len(tareas):
            tareas[numero_tarea]['completada'] = True
            guardar_tareas(tareas)
            speak(f"Tarea #{numero_tarea + 1} completada.")
            return
        else:
            speak("Número de tarea incorrecto.")
    except ValueError:
        speak("Error: El número de tarea debe ser un número entero.")

def eliminar_tarea(tareas, query):
    if not tareas:
        speak("No tienes tareas pendientes.")
        return
    
    numero_tarea = parsear_numero_elemento(query)
    while not numero_tarea:
        speak("Por favor, indica el número de la tarea que quieres eliminar.")
        numero_tarea_str = listen()
        if pattern_detener.search(numero_tarea_str):
            return
        numero_tarea = parsear_numero_elemento(numero_tarea_str)
        if not numero_tarea:
            speak("No se detectó ningún número de tarea. Por favor, intenta de nuevo.")
    
    try:
        numero_tarea = int(numero_tarea) - 1
        if 0 <= numero_tarea < len(tareas):
            del tareas[numero_tarea]
            guardar_tareas(tareas)
            speak(f"Tarea #{numero_tarea + 1} eliminada.")
            return
        else:
            speak("Número de tarea incorrecto.")
    except ValueError:
        speak("Error: El número de tarea debe ser un número entero.")


# Funciones para gestionar notas de voz (offline)
def cargar_notas():
    try:
        with open('notas.pickle', 'rb') as archivo:
            notas = pickle.load(archivo)
        return notas
    except (FileNotFoundError, pickle.UnpicklingError):
        return []
    
def guardar_notas(notas):
    with open('notas.pickle', 'wb') as archivo:
        pickle.dump(notas, archivo)

def agregar_nota(notas):
    
    nota_voz = None
    speak("Por favor, graba la nota de voz.")
    while not nota_voz:
        nota_voz = listen(tiempo_minimo=5, tiempo_maximo=60)
        if not nota_voz:
            speak("No se detectó ninguna nota de voz. ¿Quieres intentarlo de nuevo?")
            respuesta = listen()
            if respuesta.lower() in ["sí", "si"]:
                speak("Grabando la nota de voz otra vez.")
            else:
                return

    notas.append(nota_voz)
    guardar_notas(notas)
    speak("Nota de voz guardada.")

def reproducir_nota(notas, query):
    if not notas:
        speak("No tienes notas de voz guardadas.")
        return
    
    numero_nota = parsear_numero_elemento(query)
    while not numero_nota:
        speak("Por favor, indica el número de la nota que quieres reproducir.")
        numero_nota_str = listen()
        if pattern_detener.search(numero_nota_str):
            return
        numero_nota = parsear_numero_elemento(numero_nota_str)
        if not numero_nota:
            speak("No se pudo entender el número de la nota. Por favor, intenta de nuevo.")

    try:
        numero_nota = int(numero_nota) - 1
        if 0 <= numero_nota < len(notas):
            speak(f"Reproduciendo nota: {notas[numero_nota]}.")
        else:
            speak("Número de nota incorrecto.")
    except ValueError:
        speak("Error: El número de nota debe ser un número entero.")

def eliminar_nota(notas, query):
    if not notas:
        speak("No tienes notas de voz guardadas.")
        return
    
    numero_nota = parsear_numero_elemento(query)
    while not numero_nota:
        speak("Por favor, indica el número de la nota que quieres eliminar.")
        numero_nota_str = listen()
        if pattern_detener.search(numero_nota_str):
            return
        numero_nota = parsear_numero_elemento(numero_nota_str)
        if not numero_nota:
            speak("No se pudo entender el número de la nota. Por favor, intenta de nuevo.")

    try:
        numero_nota = int(numero_nota) - 1
        if 0 <= numero_nota < len(notas):
            del notas[numero_nota]
            guardar_notas(notas)
            speak(f"Nota {numero_nota+1} eliminada.")
        else:
            speak("Número de nota incorrecto.")
    except ValueError:
        speak("Error: El número de nota debe ser un número entero.")

def parsear_numero_elemento(numero_elemento_str):
    # Expresión regular para extraer el número
    patron_numero_nota = re.compile(r"\b((?:numero)?(\d+))\b", re.IGNORECASE)
    match = patron_numero_nota.search(numero_elemento_str)
    if match:
        # Comprobar los grupos de coincidencia para obtener el número correcto
        for grupo in match.groups():
            if grupo:
                numero_nota_parseado = int(grupo)
                return numero_nota_parseado
    return None


# Funciones para gestionar alarmas y temporizador (offline)
global alarma_activada
alarma_activada = False

def configurar_alarma(query):
    hora_alarma = parsear_hora(query)
    while not hora_alarma:
        speak("Por favor, indica la hora para configurar la alarma.")
        hora_alarma_str = listen()
        if pattern_detener.search(hora_alarma_str):
            return
        hora_alarma = parsear_hora(hora_alarma_str)
        if not hora_alarma:
            speak("No se pudo entender la hora. Por favor, intenta de nuevo.")
    
    speak(f"Alarma configurada para las {hora_alarma.strftime('%I:%M %p')}.")
    tiempo_alarma = calcular_tiempo_alarma(hora_alarma)
    alarma_thread = threading.Thread(target=esperar_alarma, args=(tiempo_alarma,))
    alarma_thread.start()
    # Detener otros procesos hasta que se active la alarma
    return

def calcular_tiempo_alarma(hora_alarma):
    ahora = datetime.datetime.now()
    # Convertir hora_alarma a datetime combinándolo con la fecha actual
    hora_alarma = datetime.datetime.combine(ahora.date(), hora_alarma)
    # Si la hora_alarma ya pasó hoy, establecerla para mañana
    if hora_alarma < ahora:
        hora_alarma += datetime.timedelta(days=1)
    return hora_alarma

def esperar_alarma(tiempo_alarma):
    global alarma_activada
    tiempo_restante = tiempo_alarma - datetime.datetime.now()
    segundos_restantes = tiempo_restante.total_seconds()
    time.sleep(segundos_restantes)
    alarma_activada = True

def configurar_temporizador(query):
    duracion = parsear_duracion(query)
    while not duracion:
        speak("Por favor, indica la duración para configurar el temporizador.")
        duracion_str = listen()
        if pattern_detener.search(duracion_str):
            return
        duracion = parsear_duracion(duracion_str)
        if not duracion:
            speak("No se pudo entender la duración. Por favor, intenta de nuevo.")
    

    speak(f"Temporizador configurado para {duracion} segundos.")
    temporizador_thread = threading.Thread(target=esperar_temporizador, args=(duracion,))
    temporizador_thread.start()
    # Detener otros procesos hasta que se active la alarma
    return

def esperar_temporizador(duracion_segundos):
    global alarma_activada
    time.sleep(duracion_segundos)
    alarma_activada = True

def parsear_duracion(duracion_str):
    # Expresión regular para buscar duraciones en varios formatos
    duracion_regex = r"(?:para\s*dentro\s*de|en|dentro\s*de)?\s*((\d+)\s*horas?)?\s*((\d+)\s*minutos?)?\s*((\d+)\s*segundos?)?"
    match = re.search(duracion_regex, duracion_str, re.IGNORECASE)
    if match:
        horas = int(match.group(2)) if match.group(2) else 0
        minutos = int(match.group(4)) if match.group(4) else 0
        segundos = int(match.group(6)) if match.group(6) else 0
        duracion_total_segundos = horas * 3600 + minutos * 60 + segundos
        return duracion_total_segundos
    else:
        return None

def configurar_contador(query):
    numero = parsear_numero(query)
    while not numero:
        speak("Por favor, indica el numero para configurar el contador.")
        numero_str = listen()
        if pattern_detener.search(numero_str):
            return
        numero = parsear_numero(numero_str)
        if not numero:
            speak("No se pudo entender el numero. Por favor, intenta de nuevo.")
    
    speak(f"Contando hasta {numero}.")
    for i in range(numero-1):
        speak(f"{i+1}!")
        time.sleep(1)
    speak(f"y {numero}!")
    return
                
def parsear_numero(numero):
    # Expresión regular para extraer el número
    patron_numero = re.compile(r"\b((?:hasta)?(\d+))\b", re.IGNORECASE)
    match = patron_numero.search(numero)
    if match:
        # Comprobar los grupos de coincidencia para obtener el número correcto
        for grupo in match.groups():
            if grupo:
                numero_parseado = int(grupo)
                return numero_parseado
    return None
    
def juegos(query):
    # Implementar la lógica de un juego (por ejemplo, crucigramas, sopa de letras, autocompletar)
    pass

def ayuda():
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
    
    ¡Espero que encuentres útiles estas opciones! ¿En qué puedo ayudarte hoy?
    """
    print(mensaje)
    speak(mensaje)

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
                #print("Tiempo mínimo reiniciado")
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


pattern_activacion = re.compile(r"\b(paco|opaco|pago|bajo|macho|banco)\b", re.IGNORECASE)

def main():
    agenda = cargar_agenda()
    tareas = cargar_tareas()
    notas = cargar_notas()
    global alarma_activada
    activacion = False

    while True:
        if not alarma_activada:
            query = listen(tiempo_minimo=3, tiempo_maximo=10)
        
            if query and activacion:                
                # Agenda y calendario
                if pattern_consultar_eventos.search(query):
                    consultar_eventos(agenda, query)
                elif pattern_agregar_evento.search(query):
                    agregar_evento(agenda, query)
                elif pattern_modificar_evento.search(query):
                    modificar_evento(agenda, query)
                elif pattern_eliminar_evento.search(query):
                    eliminar_evento(agenda, query)
    
                # Listas de tareas
                elif pattern_mostrar_tareas.search(query):
                    mostrar_tareas(tareas)
                elif pattern_agregar_tarea.search(query):
                    agregar_tarea(tareas, query)
                elif pattern_marcar_completada.search(query):
                    marcar_tarea_como_completada(tareas, query)
                elif pattern_eliminar_tarea.search(query):
                    eliminar_tarea(tareas, query)
    
                # Notas de voz
                elif pattern_agregar_nota.search(query):
                    agregar_nota(notas)
                elif pattern_reproducir_nota.search(query):
                    reproducir_nota(notas, query)
                elif pattern_eliminar_nota.search(query):
                    eliminar_nota(notas, query)
    
                # Alarma y temporizador
                elif pattern_consultar_hora.search(query):
                    hora_actual = datetime.datetime.now().strftime("%H:%M")
                    print(f"La hora actual es {hora_actual}.")
                    speak(f"La hora actual es {hora_actual}.")
                elif pattern_configurar_alarma.search(query):
                    configurar_alarma(query)
                elif pattern_configurar_temporizador.search(query):
                    configurar_temporizador(query)
                elif pattern_configurar_contador.search(query):
                    configurar_contador(query)
                    
                # Juegos y entretenimiento
                elif pattern_juegos.search(query):
                    juegos(query)
    
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
            elif pattern_activacion.search(query):
                print("En qué puedo ayudarte?")
                speak("¿En qué puedo ayudarte?")
                activacion = True
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
            parar = listen(tiempo_minimo=2, tiempo_maximo=2)
            if pattern_detener.search(parar):
                print("Alarma detenida.")
                speak("Alarma detenida.")
                alarma_activada = False
                activacion = False

if __name__ == "__main__":
    main()
            
