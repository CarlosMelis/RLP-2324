import speech_recognition as sr
import pyttsx3
import re
import datetime
import calendar
import pickle
import threading
import time

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
pattern_juegos = re.compile(r"\b(juegos)\b", re.IGNORECASE)
pattern_ayuda = re.compile(r"\b((ayuda|ayúdame|instrucciones|ayúdame por favor)|(consultar|ver|revisar) (?:ayuda|ayúdame|instrucciones|ayúdame por favor))\b", re.IGNORECASE)
pattern_saludo = re.compile(r"\b(hola|buenos días|buenas tardes|buenas noches)\b", re.IGNORECASE)
pattern_despedida = re.compile(r"\b(adiós|hasta luego|chao|nos vemos)\b", re.IGNORECASE)


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

def consultar_eventos(agenda):
    while True:
        if not agenda:
            speak("No hay eventos agendados.")
            return
        
        speak("¿Qué fecha deseas consultar? Puedes indicar el día, mes y/o año.")
        fecha = listen()
        fecha = parsear_fecha(fecha)
        if not fecha:
            speak("No se detectó ninguna fecha. Por favor, intenta de nuevo.")
            continue

        if not fecha:
            speak("No se pudo entender la fecha. Por favor, intenta de nuevo.")
            continue
        
        eventos_hoy = []
        for fecha_agenda, eventos in agenda.items():
            if fecha_agenda.date() == fecha.date():
                for evento in eventos:
                    eventos_hoy.append(f"{evento['hora']}: {evento['titulo']}")
        
        if not eventos_hoy:
            speak(f"No tienes eventos agendados para el {fecha.strftime('%d-%m-%Y')}. ¿Deseas consultar otro día?")
            respuesta = listen()
            if respuesta.lower() in ["sí", "si"]:
                continue
            else:
                return
        else:
            speak("Tus eventos son los siguientes:")
            for evento in eventos_hoy:
                speak(evento)
            return

def agregar_evento(agenda):
    while True:
        speak("Por favor, indica la fecha del evento. Puedes especificar el día, mes y/o año.")
        fecha = listen()
        fecha = parsear_fecha(fecha)
        if not fecha:
            speak("No se detectó ninguna fecha. Por favor, intenta de nuevo.")
            continue
        
        speak("Por favor, indica la hora del evento.")
        hora = listen()
        if not hora:
            speak("No se detectó ninguna hora. Por favor, intenta de nuevo.")
            continue
        
        speak("Por favor, indica el título del evento.")
        titulo = listen()
        if not titulo:
            speak("No se detectó ningún título. Por favor, intenta de nuevo.")
            continue
        
        break
    
    nuevo_evento = {'hora': hora, 'titulo': titulo}
    if fecha not in agenda:
        agenda[fecha] = [nuevo_evento]
    else:
        agenda[fecha].append(nuevo_evento)
    guardar_agenda(agenda)
    speak(f"Evento agregado para el {fecha.strftime('%d-%m-%Y')} a las {hora} con el título {titulo}.")


def modificar_evento(agenda):
    while True:
        speak("Por favor, indica la fecha del evento a modificar.")
        fecha = listen()
        fecha = parsear_fecha(fecha)
        if not fecha:
            speak("No se detectó ninguna fecha. ¿Quieres intentarlo de nuevo?")
            respuesta = listen()
            if respuesta.lower() in ["sí", "si"]:
                continue
            else:
                return
        
        speak(f"Eventos para el {fecha}:")
        for evento in agenda[fecha]:
            speak(f"Hora: {evento['hora']}, Título: {evento['titulo']}")
        
        speak("Por favor, indica la hora actual del evento.")
        hora_vieja = listen()
        if not hora_vieja:
            speak("No se detectó ninguna hora. ¿Quieres intentarlo de nuevo?")
            respuesta = listen()
            if respuesta.lower() in ["sí", "si"]:
                continue
            else:
                return
        
        speak("Por favor, indica la nueva hora del evento.")
        hora_nueva = listen()
        if not hora_nueva:
            speak("No se detectó ninguna hora nueva. ¿Quieres intentarlo de nuevo?")
            respuesta = listen()
            if respuesta.lower() in ["sí", "si"]:
                continue
            else:
                return
        
        break

    try:
        hora_vieja = datetime.datetime.strptime(hora_vieja, '%H:%M').time()
        hora_nueva = datetime.datetime.strptime(hora_nueva, '%H:%M').time()
    except ValueError:
        speak("Error: Formato de fecha u hora incorrecto.")
        return

    if fecha not in agenda or not any(
        evento['hora'] == hora_vieja
        for evento in agenda[fecha]
    ):
        speak(f"No se encontró el evento para el {fecha} a las {hora_vieja}.")
        return

    for i, evento in enumerate(agenda[fecha]):
        if evento['hora'] == hora_vieja:
            agenda[fecha][i] = {'hora': hora_nueva.strftime('%H:%M'), 'titulo': evento['titulo']}
            guardar_agenda(agenda)
            speak(f"Evento modificado de las {hora_vieja} a las {hora_nueva}.")
            return

def eliminar_evento(agenda):
    while True:
        speak("Por favor, indica la fecha del evento a eliminar.")
        fecha = listen()
        fecha = parsear_fecha(fecha)
        if not fecha:
            speak("No se detectó ninguna fecha. ¿Quieres intentarlo de nuevo?")
            respuesta = listen()
            if respuesta.lower() in ["sí", "si"]:
                continue
            else:
                return
        
        speak("Por favor, indica la hora del evento a eliminar.")
        hora = listen()
        if not hora:
            speak("No se detectó ninguna hora. ¿Quieres intentarlo de nuevo?")
            respuesta = listen()
            if respuesta.lower() in ["sí", "si"]:
                continue
            else:
                return
        
        speak("Por favor, indica el título del evento a eliminar.")
        titulo = listen()
        if not titulo:
            speak("No se detectó ningún título. ¿Quieres intentarlo de nuevo?")
            respuesta = listen()
            if respuesta.lower() in ["sí", "si"]:
                continue
            else:
                return
        
        break

    try:
        hora_evento = datetime.datetime.strptime(hora, '%H:%M').time()
    except ValueError:
        speak("Error: Formato de fecha u hora incorrecto.")
        return

    if fecha not in agenda or not any(
        evento['hora'] == hora_evento and evento['titulo'] == titulo
        for evento in agenda[fecha]
    ):
        speak(f"No se encontró el evento '{titulo}' para el {fecha} a las {hora}.")
        return

    for i, evento in enumerate(agenda[fecha]):
        if evento['hora'] == hora_evento and evento['titulo'] == titulo:
            del agenda[fecha][i]
            guardar_agenda(agenda)
            speak(f"Evento '{titulo}' eliminado para el {fecha} a las {hora}.")
            return

def parsear_fecha(fecha_str):
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
        speak(f"{i+1}. {descripcion}")
        speak(f"Fecha límite: {fecha_limite_str}")

def agregar_tarea(tareas):
    while True:
        speak("Por favor, indica la descripción de la tarea.")
        descripcion = listen()
        if not descripcion:
            speak("No se detectó ninguna descripción. ¿Quieres intentarlo de nuevo?")
            respuesta = listen()
            if respuesta.lower() in ["sí", "si"]:
                continue
            else:
                return
        
        speak("¿Hay una fecha límite para esta tarea? Indica la fecha en formato día-mes-año, o simplemente di no hay fecha límite.")
        fecha_limite = listen()
        if fecha_limite.lower() == "no hay fecha límite":
            fecha_limite = ""
        elif not fecha_limite:
            speak("No se detectó ninguna fecha límite. ¿Quieres intentarlo de nuevo?")
            respuesta = listen()
            if respuesta.lower() in ["sí", "si"]:
                continue
            else:
                return
        else:
            try:
                fecha_limite = parsear_fecha(fecha_limite)
                fecha_limite = datetime.datetime.strptime(fecha_limite, '%d-%m-%Y').date()
            except ValueError:
                speak("Error: Formato de fecha incorrecto. ¿Quieres intentarlo de nuevo?")
                respuesta = listen()
                if respuesta.lower() in ["sí", "si"]:
                    continue
                else:
                    return
        
        break

    nueva_tarea = {'descripcion': descripcion, 'fecha_limite': fecha_limite, 'completada': False}
    tareas.append(nueva_tarea)
    guardar_tareas(tareas)
    speak(f"Tarea '{descripcion}' agregada.")

def marcar_tarea_como_completada(tareas):
    while True:
        speak("Por favor, indica el número de la tarea que quieres marcar como completada.")
        numero_tarea = listen()
        if not numero_tarea:
            speak("No se detectó ningún número de tarea. ¿Quieres intentarlo de nuevo?")
            respuesta = listen()
            if respuesta.lower() in ["sí", "si"]:
                continue
            else:
                return
        
        break

    if not tareas:
        speak("No tienes tareas pendientes.")
        return

    try:
        numero_tarea = int(numero_tarea) - 1
        if 0 <= numero_tarea < len(tareas):
            tareas[numero_tarea]['completada'] = True
            guardar_tareas(tareas)
            speak(f"Tarea #{numero_tarea+1} completada.")
        else:
            speak("Número de tarea incorrecto.")
    except ValueError:
        speak("Error: El número de tarea debe ser un número entero.")

def eliminar_tarea(tareas):
    while True:
        speak("Por favor, indica el número de la tarea que quieres eliminar.")
        numero_tarea = listen()
        if not numero_tarea:
            speak("No se detectó ningún número de tarea. ¿Quieres intentarlo de nuevo?")
            respuesta = listen()
            if respuesta.lower() in ["sí", "si"]:
                continue
            else:
                return
        
        break

    if not tareas:
        speak("No tienes tareas pendientes.")
        return

    try:
        numero_tarea = int(numero_tarea) - 1
        if 0 <= numero_tarea < len(tareas):
            del tareas[numero_tarea]
            guardar_tareas(tareas)
            speak(f"Tarea #{numero_tarea+1} eliminada.")
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
    while True:
        speak("Por favor, graba la nota de voz.")
        nota_voz = listen()
        if not nota_voz:
            speak("No se detectó ninguna nota de voz. ¿Quieres intentarlo de nuevo?")
            respuesta = listen()
            if respuesta.lower() in ["sí", "si"]:
                continue
            else:
                return
        
        break

    notas.append(nota_voz)
    guardar_notas(notas)
    speak("Nota de voz guardada.")

def reproducir_nota(notas):
    while True:
        speak("Por favor, indica el número de la nota que quieres reproducir.")
        numero_nota = listen()
        if not numero_nota:
            speak("No se detectó ningún número de nota. ¿Quieres intentarlo de nuevo?")
            respuesta = listen()
            if respuesta.lower() in ["sí", "si"]:
                continue
            else:
                return
        
        break

    if not notas:
        speak("No tienes notas de voz guardadas.")
        return

    try:
        numero_nota = int(numero_nota) - 1
        if 0 <= numero_nota < len(notas):
            speak(f"Reproduciendo nota: {notas[numero_nota]}.")
        else:
            speak("Número de nota incorrecto.")
    except ValueError:
        speak("Error: El número de nota debe ser un número entero.")

def eliminar_nota(notas):
    while True:
        speak("Por favor, indica el número de la nota que quieres eliminar.")
        numero_nota = listen()
        if not numero_nota:
            speak("No se detectó ningún número de nota. ¿Quieres intentarlo de nuevo?")
            respuesta = listen()
            if respuesta.lower() in ["sí", "si"]:
                continue
            else:
                return
        
        break

    if not notas:
        speak("No tienes notas de voz guardadas.")
        return

    try:
        numero_nota = int(numero_nota) - 1
        if 0 <= numero_nota < len(notas):
            del notas[numero_nota]
            guardar_notas(notas)
            speak(f"Nota #{numero_nota+1} eliminada.")
        else:
            speak("Número de nota incorrecto.")
    except ValueError:
        speak("Error: El número de nota debe ser un número entero.")

# Funciones para gestionar alarmas y temporizador (offline)
global alarma_activada
alarma_activada = False

def configurar_alarma():
    while True:
        speak("Por favor, indica la hora para configurar la alarma.")
        hora = listen()
        if not hora:
            speak("No se detectó ninguna hora. ¿Quieres intentarlo de nuevo?")
            respuesta = listen()
            if respuesta.lower() in ["sí", "si"]:
                continue
            else:
                return
        
        hora_alarma = parsear_hora(hora)
        if hora_alarma:
            speak(f"Alarma configurada para las {hora_alarma.strftime('%I:%M %p')}.")
            tiempo_alarma = calcular_tiempo_alarma(hora_alarma)
            alarma_thread = threading.Thread(target=esperar_alarma, args=(tiempo_alarma,))
            alarma_thread.start()
            # Detener otros procesos hasta que se active la alarma
            while not alarma_activada:
                pass
            return
        else:
            speak("No se pudo entender la hora. Por favor, intenta de nuevo.")

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

def parsear_hora(hora_str):
    # Expresión regular para buscar horas en varios formatos
    hora_regex = r"(?:a(?: las)?\s*)?(?:(\d{1,2}):(\d{2})(?:\s*(?:de la)?\s*(mañana|tarde|noche))|(?:en|dentro de)\s*(\d+)\s*(horas?|minutos?|segundos?))"
    match = re.search(hora_regex, hora_str, re.IGNORECASE)
    if match:
        if match.group(1) and match.group(2) and match.group(3):  # Hora específica
            hora = int(match.group(1))
            minutos = int(match.group(2))
            periodo = match.group(3)
        elif match.group(4) and match.group(5):  # Tiempo futuro
            horas = 0
            minutos = 0
            segundos = 0
            if match.group(5).lower().startswith('h'):  # Horas
                horas = int(match.group(4))
            elif match.group(5).lower().startswith('m'):  # Minutos
                minutos = int(match.group(4))
            elif match.group(5).lower().startswith('s'):  # Segundos
                segundos = int(match.group(4))
            # Calcular tiempo futuro
            tiempo_futuro = datetime.datetime.now() + datetime.timedelta(hours=horas, minutes=minutos, seconds=segundos)
            return tiempo_futuro.time()
        else:
            return None
        
        if periodo:
            periodo = periodo.lower()
            if periodo == "mañana":
                if hora == 12:
                    hora = 0
            elif periodo == "tarde":
                if hora < 12:
                    hora += 12
        else:
            if hora >= 12:
                periodo = "tarde"
            else:
                periodo = "mañana"
                
        return datetime.datetime.now().replace(hour=hora, minute=minutos, second=0)
    else:
        try:
            return datetime.datetime.strptime(hora_str, '%I:%M %p').time()
        except ValueError:
            return None

def configurar_temporizador():
    while True:
        speak("Por favor, indica la duración para configurar el temporizador.")
        duracion = listen()
        if not duracion:
            speak("No se detectó ninguna duración. ¿Quieres intentarlo de nuevo?")
            respuesta = listen()
            if respuesta.lower() in ["sí", "si"]:
                continue
            else:
                return
        
        duracion_segundos = parsear_duracion(duracion)
        if duracion_segundos is not None:
            speak(f"Temporizador configurado para {duracion_segundos} segundos.")
            temporizador_thread = threading.Thread(target=esperar_temporizador, args=(duracion_segundos,))
            temporizador_thread.start()
            # Detener otros procesos hasta que se active la alarma
            while not alarma_activada:
                pass
            return
        else:
            speak("No se pudo entender la duración. Por favor, intenta de nuevo.")

def esperar_temporizador(duracion_segundos):
    global alarma_activada
    time.sleep(duracion_segundos)
    alarma_activada = True

def parsear_duracion(duracion_str):
    # Expresión regular para buscar duraciones en varios formatos
    duracion_regex = r"((\d+)\s+horas?)?\s*((\d+)\s+minutos?)?\s*((\d+)\s+segundos?)?"
    match = re.search(duracion_regex, duracion_str, re.IGNORECASE)
    if match:
        horas = int(match.group(2)) if match.group(2) else 0
        minutos = int(match.group(4)) if match.group(4) else 0
        segundos = int(match.group(6)) if match.group(6) else 0
        duracion_total_segundos = horas * 3600 + minutos * 60 + segundos
        return duracion_total_segundos
    else:
        return None

def configurar_contador():
    while True:
        speak("Por favor, indica el numero para configurar el contador.")
        numero = listen()
        if not numero:
            speak("No se detectó ningun numero. ¿Quieres intentarlo de nuevo?")
            respuesta = listen()
            if respuesta.lower() in ["sí", "si"]:
                continue
            else:
                return
            
        numero = parsear_numero(numero)
        if numero is not None:
            speak(f"Contando hasta {numero}.")
            for i in range(numero):
                speak(f"{i+1}")
                time.sleep(1)
            return
        else:
            speak("No se pudo entender el numero. Por favor, intenta de nuevo.")
                
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
    
def juegos():
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
recognizer = sr.Recognizer()
def listen(timeout=1, phrase_time_limit=5):
    try:
        with sr.Microphone() as source:
            print("Escuchando...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            query = recognizer.recognize_google(audio, language='es-ES')  
            print(f"¿Has dicho: {query}?")
            return query.lower()
    except:
        return ""

pattern_activacion = re.compile(r"\b(paco)\b", re.IGNORECASE)

if __name__ == "__main__":
    agenda = cargar_agenda()
    tareas = cargar_tareas()
    notas = cargar_notas()
    
    activacion = False

    while True:
        if not alarma_activada:
            query = listen(timeout=3, phrase_time_limit=3)
        
            if query and activacion:                
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
                    juegos()
    
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
            parar = listen(timeout=0.5, phrase_time_limit=1)
            if parar == "para":
                print("Alarma detenida.")
                speak("Alarma detenida.")
                alarma_activada = False
            
