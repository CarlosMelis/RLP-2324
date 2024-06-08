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
from playsound import playsound  # Asegúrate de tener instalada esta librería para reproducir sonido
from PIL import Image, ImageTk   # Asegúrate de tener instalada esta librería para manipulación de imágenes
import glob
import random

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
pattern_agregar_evento = re.compile(r"\b(agregar|crear|insertar|añadir|poner|añade|crea) ?(1 ?(nuevo)?)? (evento)\b", re.IGNORECASE)
pattern_modificar_evento = re.compile(r"\b(modificar|editar|cambiar) ?(el|1)? (evento)\b", re.IGNORECASE)
pattern_eliminar_evento = re.compile(r"\b(eliminar|quitar|borrar) ?(el|1)? (evento)\b", re.IGNORECASE)

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

# Juegos y terapias
pattern_terapia = re.compile(r"\b(terapia)\b", re.IGNORECASE)
pattern_juegos = re.compile(r"\b(jugar|juego)\b", re.IGNORECASE)
pattern_remember = re.compile(r"\b(recordar)\b", re.IGNORECASE)
pattern_af = re.compile(r"\b(atención|focal)\b", re.IGNORECASE)
pattern_bv = re.compile(r"\b(busqueda|visual)\b", re.IGNORECASE)
pattern_c = re.compile(r"\b(concentración)\b", re.IGNORECASE)

# Otros
pattern_ayuda = re.compile(r"\b(ayuda|ayúdame|instrucciones)\b", re.IGNORECASE)
pattern_saludo = re.compile(r"\b(hola|buenos días|buenas tardes|buenas noches)\b", re.IGNORECASE)
pattern_despedida = re.compile(r"\b(adiós|hasta luego|chao|nos vemos)\b", re.IGNORECASE)
pattern_detener = re.compile(r"\b(para|basta|detente|termina|atras|retroceder|atrás|salir)\b", re.IGNORECASE)

# Sistema
pattern_cambiar_color = re.compile(r"\b(cambiar|poner|configurar) ?(el|la)? (fondo|pantalla|tema) ?(a)?\b", re.IGNORECASE)

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
    while True:
        if not agenda:
            label_info.config(text="No hay eventos agendados.")
            ajustar_tamaño_texto()
            speak("No hay eventos agendados.")
            return
    
        fecha = parsear_fecha(query)
        if fecha:
            label_info.config(text="Estas seguro de esta fecha?")
            ajustar_tamaño_texto()
            speak("Estas seguro de esta fecha?")
            label_info.config(text=fecha.strftime('%d-%m-%Y'))
            ajustar_tamaño_texto()
            speak(fecha.strftime('%d-%m-%Y'))
            
            text = 'Di "si" para confirmar esta fecha'
            respuesta = listen(advice_text=text)
            if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
                fecha = None
        
        while not fecha:
            label_info.config(text="¿Qué fecha deseas consultar? Puedes indicar el día, mes y/o año.")
            ajustar_tamaño_texto()
            speak("¿Qué fecha deseas consultar? Puedes indicar el día, mes y/o año.")
            
            text = 'Si no quieres continuar puedes decir "basta" o "salir" para volver al asistente'
            fecha_str = listen(advice_text=text)
            if pattern_detener.search(fecha_str):
                return
            fecha = parsear_fecha(fecha_str)
            if not fecha:
                label_info.config(text="No se detectó ninguna fecha. Por favor, intenta de nuevo.")
                ajustar_tamaño_texto()
                speak("No se detectó ninguna fecha. Por favor, intenta de nuevo.")
            else:
                label_info.config(text="Estas seguro de esta fecha?")
                ajustar_tamaño_texto()
                speak("Estas seguro de esta fecha?")
                label_info.config(text=fecha.strftime('%d-%m-%Y'))
                ajustar_tamaño_texto()
                speak(fecha.strftime('%d-%m-%Y'))
                
                text = 'Di "si" para confirmar esta fecha'
                respuesta = listen(advice_text=text)
                if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
                    fecha = None
        
        eventos_hoy = []
        for fecha_agenda, eventos in agenda.items():
            if fecha_agenda.date() == fecha.date():
                for evento in eventos:
                    eventos_hoy.append(f"{evento['hora']}: {evento['titulo']}")
        
        if not eventos_hoy:
            label_info.config(text=f"No tienes eventos agendados para el {fecha.strftime('%d-%m-%Y')}. ¿Deseas consultar otro día?")
            ajustar_tamaño_texto()
            speak(f"No tienes eventos agendados para el {fecha.strftime('%d-%m-%Y')}. ¿Deseas consultar otro día?")
            
            text = 'Di "si" para consultar otro día'
            respuesta = listen(advice_text=text)
            if re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
                query = ""
            else:
                return
        else:
            label_info.config(text="Tus eventos son los siguientes:")
            ajustar_tamaño_texto()
            speak("Tus eventos son los siguientes:")
            for evento in eventos_hoy:
                label_info.config(text=evento)
                ajustar_tamaño_texto()
                speak(evento)
            return

def agregar_evento(agenda, query):
    fecha = parsear_fecha(query)
    if fecha:
        label_info.config(text="Estas seguro de esta fecha?")
        ajustar_tamaño_texto()
        speak("Estas seguro de esta fecha?")
        label_info.config(text=fecha.strftime('%d-%m-%Y'))
        ajustar_tamaño_texto()
        speak(fecha.strftime('%d-%m-%Y'))
        
        text = 'Di "si" para confirmar esta fecha'
        respuesta = listen(advice_text=text)
        if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
            fecha = None
    
    while not fecha:
        label_info.config(text="Por favor, indica la fecha del evento. Puedes especificar el día, mes y/o año.")
        ajustar_tamaño_texto()
        speak("Por favor, indica la fecha del evento. Puedes especificar el día, mes y/o año.")
        
        text = 'Si no quieres continuar puedes decir "retroceder" o "salir" para volver al asistente'
        fecha_str = listen(advice_text=text)
        if pattern_detener.search(fecha_str):
            return
        fecha = parsear_fecha(fecha_str)
        if not fecha:
            label_info.config(text="No se detectó ninguna fecha. Por favor, intenta de nuevo.")
            ajustar_tamaño_texto()
            speak("No se detectó ninguna fecha. Por favor, intenta de nuevo.")
        else:
            label_info.config(text="Estas seguro de esta fecha?")
            ajustar_tamaño_texto()
            speak("Estas seguro de esta fecha?")
            label_info.config(text=fecha.strftime('%d-%m-%Y'))
            ajustar_tamaño_texto()
            speak(fecha.strftime('%d-%m-%Y'))
            
            text = 'Di "si" para confirmar esta fecha'
            respuesta = listen(advice_text=text)
            if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
                fecha = None
    
    hora = parsear_hora(query)
    if hora:
        label_info.config(text="Estas seguro de esta hora?")
        ajustar_tamaño_texto()
        speak("Estas seguro de esta hora?")
        label_info.config(text=hora.strftime('%H:%M'))
        ajustar_tamaño_texto()
        speak(hora.strftime('%H:%M'))
        
        text = 'Di "si" para confirmar esta hora'
        respuesta = listen(advice_text=text)
        if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
            hora = None
    
    while not hora:
        label_info.config(text="Por favor, indica la hora del evento.")
        ajustar_tamaño_texto()
        speak("Por favor, indica la hora del evento.")
        
        text = 'Si no quieres continuar puedes decir "atras" o "para" para volver al asistente'
        hora_str = listen(advice_text=text)
        if pattern_detener.search(hora_str):
            return
        hora = parsear_fecha(hora_str)
        if not hora:
            label_info.config(text="No se detectó ninguna hora. Por favor, intenta de nuevo.")
            ajustar_tamaño_texto()
            speak("No se detectó ninguna hora. Por favor, intenta de nuevo.")
        else:
            label_info.config(text="Estas seguro de esta hora?")
            ajustar_tamaño_texto()
            speak("Estas seguro de esta hora?")
            label_info.config(text=hora.strftime('%H:%M'))
            ajustar_tamaño_texto()
            speak(hora.strftime('%H:%M'))
            
            text = 'Di "si" para confirmar esta hora'
            respuesta = listen(advice_text=text)
            if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
                hora = None
    
    titulo = None
    while not titulo:
        label_info.config(text="Por favor, indica el título del evento.")
        ajustar_tamaño_texto()
        speak("Por favor, indica el título del evento.")
        
        text = 'Si no quieres continuar puedes decir "salir" o "basta" para volver al asistente'
        titulo = listen(tiempo_minimo=5, tiempo_maximo=60, advice_text=text)
        if pattern_detener.search(titulo):
            return
        if not titulo:
            label_info.config(text="No se detectó ningún título. Por favor, intenta de nuevo.")
            ajustar_tamaño_texto()
            speak("No se detectó ningún título. Por favor, intenta de nuevo.") 
        else:
            label_info.config(text="Estas seguro de este titulo?")
            ajustar_tamaño_texto()
            speak("Estas seguro de este titulo?")
            label_info.config(text=titulo)
            ajustar_tamaño_texto()
            speak(titulo)
            
            text = 'Di "si" para confirmar este título'
            respuesta = listen(advice_text=text)
            if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
                titulo = None
    
    nuevo_evento = {'hora': hora.strftime('%H:%M'), 'titulo': titulo}
    fecha_str = fecha.strftime('%Y-%m-%d')
    if fecha_str not in agenda:
        agenda[fecha_str] = [nuevo_evento]
    else:
        agenda[fecha_str].append(nuevo_evento)
    guardar_agenda(agenda)
    label_info.config(text=f"Evento agregado para el {fecha.strftime('%d-%m-%Y')} a las {hora.strftime('%H:%M')} con el título {titulo}.")
    ajustar_tamaño_texto()
    speak(f"Evento agregado para el {fecha.strftime('%d-%m-%Y')} a las {hora.strftime('%H:%M')} con el título {titulo}.")


def modificar_evento(agenda, query):
    if not agenda:
        label_info.config(text="No hay eventos agendados.")
        ajustar_tamaño_texto()
        speak("No hay eventos agendados.")
        return
    
    fecha = parsear_fecha(query)
    if fecha:
        label_info.config(text="Estas seguro de esta fecha?")
        ajustar_tamaño_texto()
        speak("Estas seguro de esta fecha?")
        label_info.config(text=fecha.strftime('%d-%m-%Y'))
        ajustar_tamaño_texto()
        speak(fecha.strftime('%d-%m-%Y'))
        
        text = 'Di "si" para confirmar esta fecha'
        respuesta = listen(advice_text=text)
        if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
            fecha = None
    
    while not fecha:
        label_info.config(text="Por favor, indica la fecha del evento a modificar.")
        ajustar_tamaño_texto()
        speak("Por favor, indica la fecha del evento a modificar.")
        
        text = 'Si no quieres continuar puedes decir "para" o "basta" para volver al asistente'
        fecha_str = listen(advice_text=text)
        if pattern_detener.search(fecha_str):
            return
        fecha = parsear_fecha(fecha_str)
        if not fecha:
            label_info.config(text="No se detectó ninguna fecha. Por favor, intenta de nuevo.")
            ajustar_tamaño_texto()
            speak("No se detectó ninguna fecha. Por favor, intenta de nuevo.")
        else:
            label_info.config(text="Estas seguro de esta fecha?")
            ajustar_tamaño_texto()
            speak("Estas seguro de esta fecha?")
            label_info.config(text=fecha.strftime('%d-%m-%Y'))
            ajustar_tamaño_texto()
            speak(fecha.strftime('%d-%m-%Y'))
            
            text = 'Di "si" para confirmar esta fecha'
            respuesta = listen(advice_text=text)
            if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
                fecha = None
    
    if fecha not in agenda:
        label_info.config(text=f"No hay eventos para el {fecha.strftime('%d-%m-%Y')}.")
        ajustar_tamaño_texto()
        speak(f"No hay eventos para el {fecha.strftime('%d-%m-%Y')}.")
        return
    
    label_info.config(text=f"Eventos para el {fecha.strftime('%d-%m-%Y')}:")
    ajustar_tamaño_texto()
    speak(f"Eventos para el {fecha.strftime('%d-%m-%Y')}:")
    for evento in agenda[fecha]:
        label_info.config(text=f"Hora: {evento['hora']}, Título: {evento['titulo']}")
        ajustar_tamaño_texto()
        speak(f"Hora: {evento['hora']}, Título: {evento['titulo']}")
    
    hora_vieja = None
    while not hora_vieja:
        label_info.config(text="Por favor, indica la hora actual del evento.")
        ajustar_tamaño_texto()
        speak("Por favor, indica la hora actual del evento.")
        
        text = 'Si no quieres continuar puedes decir "detente" o "retroceder" para volver al asistente'
        hora_vieja_str = listen(advice_text=text)
        if pattern_detener.search(hora_vieja_str):
            return
        hora_vieja = parsear_hora(hora_vieja_str)
        if not hora_vieja:
            label_info.config(text="No se detectó ninguna hora actual. Por favor, intenta de nuevo.")
            ajustar_tamaño_texto()
            speak("No se detectó ninguna hora actual. Por favor, intenta de nuevo.")
        else:
            label_info.config(text="Estas seguro de esta hora?")
            ajustar_tamaño_texto()
            speak("Estas seguro de esta hora?")
            label_info.config(text=hora_vieja.strftime('%H:%M'))
            ajustar_tamaño_texto()
            speak(hora_vieja.strftime('%H:%M'))
            
            text = 'Di "si" para confirmar esta vieja hora'
            respuesta = listen(advice_text=text)
            if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
                hora_vieja = None

    hora_nueva = None
    while not hora_nueva:
        label_info.config(text="Por favor, indica la nueva hora del evento.")
        ajustar_tamaño_texto()
        speak("Por favor, indica la nueva hora del evento.")
        
        text = 'Si no quieres continuar puedes decir "atras" o "retroceder" para volver al asistente'
        hora_nueva_str = listen(advice_text=text)
        if pattern_detener.search(hora_nueva_str):
            return
        hora_nueva = parsear_hora(hora_nueva_str)
        if not hora_nueva:
            label_info.config(text="No se detectó ninguna hora nueva. Por favor, intenta de nuevo.")
            ajustar_tamaño_texto()
            speak("No se detectó ninguna hora nueva. Por favor, intenta de nuevo.")
        else:
            label_info.config(text="Estas seguro de esta hora?")
            ajustar_tamaño_texto()
            speak("Estas seguro de esta hora?")
            label_info.config(text=hora_nueva.strftime('%H:%M'))
            ajustar_tamaño_texto()
            speak(hora_nueva.strftime('%H:%M'))
            
            text = 'Di "si" para confirmar esta nueva hora'
            respuesta = listen(advice_text=text)
            if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
                hora_nueva = None

    try:
        hora_vieja = hora_vieja.strftime('%H:%M')
        hora_nueva = hora_nueva.strftime('%H:%M')
    except ValueError:
        label_info.config(text="Error: Formato de fecha u hora incorrecto.")
        ajustar_tamaño_texto()
        speak("Error: Formato de fecha u hora incorrecto.")
        return

    for i, evento in enumerate(agenda[fecha]):
        if evento['hora'] == hora_vieja:
            agenda[fecha][i] = {'hora': hora_nueva, 'titulo': evento['titulo']}
            guardar_agenda(agenda)
            label_info.config(text=f"Evento modificado de las {hora_vieja} a las {hora_nueva}.")
            ajustar_tamaño_texto()
            speak(f"Evento modificado de las {hora_vieja} a las {hora_nueva}.")
            return

def eliminar_evento(agenda, query):
    if not agenda:
        label_info.config(text="No hay eventos agendados.")
        ajustar_tamaño_texto()
        speak("No hay eventos agendados.")
        return
    
    fecha = parsear_fecha(query)
    if fecha:
        label_info.config(text="Estas seguro de esta fecha limite?")
        ajustar_tamaño_texto()
        speak("Estas seguro de esta fecha limite?")
        label_info.config(text=fecha.strftime('%d-%m-%Y'))
        ajustar_tamaño_texto()
        speak(fecha.strftime('%d-%m-%Y'))
        
        text = 'Di "si" para confirmar esta hora'
        respuesta = listen(advice_text=text)
        if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
            fecha = None
    
    while not fecha:
        label_info.config(text="Por favor, indica la fecha del evento a eliminar.")
        ajustar_tamaño_texto()
        speak("Por favor, indica la fecha del evento a eliminar.")
        
        text = 'Si no quieres continuar puedes decir "basta" o "detener" para volver al asistente'
        fecha_str = listen(advice_text=text)
        if pattern_detener.search(fecha_str):
            return
        fecha = parsear_fecha(fecha_str)
        if not fecha:
            label_info.config(text="No se detectó ninguna fecha. Por favor, intenta de nuevo.")
            ajustar_tamaño_texto()
            speak("No se detectó ninguna fecha. Por favor, intenta de nuevo.")
        else:
            label_info.config(text="Estas seguro de esta fecha?")
            ajustar_tamaño_texto()
            speak("Estas seguro de esta fecha?")
            label_info.config(text=fecha.strftime('%d-%m-%Y'))
            ajustar_tamaño_texto()
            speak(fecha.strftime('%d-%m-%Y'))
            
            text = 'Di "si" para confirmar esta fecha'
            respuesta = listen(advice_text=text)
            if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
                fecha = None

    if fecha not in agenda:
        label_info.config(text=f"No hay eventos para el {fecha.strftime('%d-%m-%Y')}.")
        ajustar_tamaño_texto()
        speak(f"No hay eventos para el {fecha.strftime('%d-%m-%Y')}.")
        return

    hora = None
    while not hora:
        label_info.config(text="Por favor, indica la hora del evento a eliminar.")
        ajustar_tamaño_texto()
        speak("Por favor, indica la hora del evento a eliminar.")
        
        text = 'Si no quieres continuar puedes decir "atras" o "salir" para volver al asistente'
        hora_str = listen(advice_text=text)
        if pattern_detener.search(hora_str):
            return
        hora = parsear_hora(hora_str)
        if not hora:
            label_info.config(text="No se detectó ninguna hora. Por favor, intenta de nuevo.")
            ajustar_tamaño_texto()
            speak("No se detectó ninguna hora. Por favor, intenta de nuevo.")
        else:
            label_info.config(text="Estas seguro de esta hora?")
            ajustar_tamaño_texto()
            speak("Estas seguro de esta hora?")
            label_info.config(text=hora.strftime('%H:%M'))
            ajustar_tamaño_texto()
            speak(hora.strftime('%H:%M'))
            
            text = 'Di "si" para confirmar esta hora'
            respuesta = listen(advice_text=text)
            if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
                hora = None

    try:
        hora_evento = hora.strftime('%H:%M')
    except ValueError:
        label_info.config(text="Error: Formato de hora incorrecto.")
        ajustar_tamaño_texto()
        speak("Error: Formato de hora incorrecto.")
        return

    if not any(evento['hora'] == hora_evento for evento in agenda[fecha]):
        label_info.config(text=f"No se encontró el evento para el {fecha.strftime('%d-%m-%Y')} a las {hora_evento}.")
        ajustar_tamaño_texto()
        speak(f"No se encontró el evento para el {fecha.strftime('%d-%m-%Y')} a las {hora_evento}.")
        return

    for i, evento in enumerate(agenda[fecha]):
        if evento['hora'] == hora_evento:
            label_info.config(text="Estas seguro de eliminar este evento?")
            ajustar_tamaño_texto()
            speak("Estas seguro de eliminar este evento?")
            label_info.config(text=f"Hora: {evento['hora']}, Título: {evento['titulo']}")
            ajustar_tamaño_texto()
            speak(f"Hora: {evento['hora']}, Título: {evento['titulo']}")
            
            text = 'Di "si" para eliminar este evento'
            respuesta = listen(advice_text=text)
            if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
                return
            del agenda[fecha][i]
            if not agenda[fecha]:
                del agenda[fecha]
            guardar_agenda(agenda)
            label_info.config(text=f"Evento eliminado para el {fecha.strftime('%d-%m-%Y')} a las {hora_evento}.")
            ajustar_tamaño_texto()
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
        label_info.config(text="No tienes tareas en la lista.")
        ajustar_tamaño_texto()
        speak("No tienes tareas en la lista.")
        return
    
    label_info.config(text="Tus tareas pendientes:")
    ajustar_tamaño_texto()
    speak("Tus tareas pendientes:")
    for i, tarea in enumerate(tareas):
        descripcion = tarea['descripcion']
        fecha_limite_str = tarea['fecha_limite'].strftime('%d-%m-%Y') if tarea['fecha_limite'] else "Sin fecha límite"
        estado = "Completada" if tarea.get('completada', False) else "Pendiente"
        label_info.config(text=f"{i+1}. {descripcion}")
        ajustar_tamaño_texto()
        speak(f"{i+1}. {descripcion}")
        label_info.config(text=f"Fecha límite: {fecha_limite_str} - Estado: {estado}")
        ajustar_tamaño_texto()
        speak(f"Fecha límite: {fecha_limite_str} - Estado: {estado}")

def agregar_tarea(tareas, query):

    descripcion = None
    while not descripcion:
        label_info.config(text="Por favor, indica la descripción de la tarea.")
        ajustar_tamaño_texto()
        speak("Por favor, indica la descripción de la tarea.")
        
        text = 'Si no quieres continuar puedes decir "detente" o "terminar" para volver al asistente'
        descripcion_str = listen(tiempo_minimo=5, tiempo_maximo=60, advice_text=text)
        if pattern_detener.search(descripcion_str):
            return
        descripcion = descripcion_str
        if not descripcion:
            label_info.config(text="No se detectó ninguna descripción. Por favor, intenta de nuevo.")
            ajustar_tamaño_texto()
            speak("No se detectó ninguna descripción. Por favor, intenta de nuevo.")
        else:
            label_info.config(text="Estas seguro de esta descripcion?")
            ajustar_tamaño_texto()
            speak("Estas seguro de esta descripcion?")
            label_info.config(text=descripcion)
            ajustar_tamaño_texto()
            speak(descripcion)
            
            text = 'Di "si" para confirmar esta descripcion'
            respuesta = listen(advice_text=text)
            if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
                descripcion = None
    
    if re.compile(r"((sin|no ?(hay)?) ?(tiempo|fecha)? limite)", re.IGNORECASE).search(query):
        fecha_limite = "ninguna"
    else:
        fecha_limite = parsear_fecha(query)
        
    if fecha_limite:
        label_info.config(text="Estas seguro de esta fecha limite?")
        ajustar_tamaño_texto()
        speak("Estas seguro de esta fecha limite?")
        fecha_limite_str = fecha_limite.strftime('%d-%m-%Y') if fecha_limite else "Sin fecha límite"
        label_info.config(text=fecha_limite_str)
        ajustar_tamaño_texto()
        speak(fecha_limite_str)
        
        text = 'Di "si" para confirmar esta fecha limite'
        respuesta = listen(advice_text=text)
        if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
            fecha_limite = None

    while not fecha_limite:
       label_info.config(text="¿Hay una fecha límite para esta tarea? Indica la fecha en formato día-mes-año, o simplemente di no hay fecha límite.")
       ajustar_tamaño_texto()
       speak("¿Hay una fecha límite para esta tarea? Indica la fecha en formato día-mes-año, o simplemente di no hay fecha límite.")
       
       text = 'Si no quieres continuar puedes decir "salir" o "basta" para volver al asistente'
       fecha_limite_str = listen(advice_text=text)
       if pattern_detener.search(fecha_limite_str):
           return

       if re.compile(r"((sin|no ?(hay)?) ?(tiempo|fecha)? limite)", re.IGNORECASE).search(fecha_limite_str):
           fecha_limite = "ninguna"
       else:
           fecha_limite = parsear_fecha(fecha_limite_str)
           
       if not fecha_limite:
           label_info.config(text="No se detectó ninguna fecha límite. Por favor, intenta de nuevo.")
           ajustar_tamaño_texto()
           speak("No se detectó ninguna fecha límite. Por favor, intenta de nuevo.")    
       else:
           label_info.config(text="Estas seguro de esta fecha limite?")
           ajustar_tamaño_texto()
           speak("Estas seguro de esta fecha limite?")
           fecha_limite_str = fecha_limite.strftime('%d-%m-%Y') if fecha_limite else "Sin fecha límite"
           label_info.config(text=fecha_limite_str)
           ajustar_tamaño_texto()
           speak(fecha_limite_str)
           
           text = 'Di "si" para confirmar esta fecha limite'
           respuesta = listen(advice_text=text)
           if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
               fecha_limite = None

    nueva_tarea = {'descripcion': descripcion, 'fecha_limite': fecha_limite, 'completada': False}
    tareas.append(nueva_tarea)
    guardar_tareas(tareas)
    label_info.config(text=f"Tarea '{descripcion}' agregada.")
    ajustar_tamaño_texto()
    speak(f"Tarea '{descripcion}' agregada.")

def marcar_tarea_como_completada(tareas, query):
    if not tareas:
        label_info.config(text="No tienes tareas pendientes.")
        ajustar_tamaño_texto()
        speak("No tienes tareas pendientes.")
        return
    
    numero_tarea = parsear_numero_elemento(query)
    while not numero_tarea:
        label_info.config(text="Por favor, indica el número de la tarea que quieres marcar como completada.")
        ajustar_tamaño_texto()
        speak("Por favor, indica el número de la tarea que quieres marcar como completada.")
        
        text = 'Si no quieres continuar puedes decir "salir" o "para" para volver al asistente'
        numero_tarea_str = listen(advice_text=text)
        if pattern_detener.search(numero_tarea_str):
            return
        numero_tarea = parsear_numero_elemento(numero_tarea_str)
        if not numero_tarea:
            label_info.config(text="No se detectó ningún número de tarea. Por favor, intenta de nuevo.")
            ajustar_tamaño_texto()
            speak("No se detectó ningún número de tarea. Por favor, intenta de nuevo.")
    
    try:
        numero_tarea = int(numero_tarea) - 1
        if 0 <= numero_tarea < len(tareas) and not tareas[numero_tarea]['completada']:
            label_info.config(text="Estas seguro de marcar como completada esta tarea?")
            ajustar_tamaño_texto()
            speak("Estas seguro de marcar como completada esta tarea?")
            descripcion = tareas[numero_tarea]['descripcion']
            fecha_limite_str = tareas[numero_tarea]['fecha_limite'].strftime('%d-%m-%Y') if tareas[numero_tarea]['fecha_limite'] else "Sin fecha límite"
            estado = "Completada" if tareas[numero_tarea].get('completada', False) else "Pendiente"
            label_info.config(text=f"{numero_tarea}. {descripcion}")
            ajustar_tamaño_texto()
            speak(f"{numero_tarea}. {descripcion}")
            label_info.config(text=f"Fecha límite: {fecha_limite_str} - Estado: {estado}")
            ajustar_tamaño_texto()
            speak(f"Fecha límite: {fecha_limite_str} - Estado: {estado}")
            
            text = 'Di "si" para marcar como completada esta tarea'
            respuesta = listen(advice_text=text)
            if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
                return
            tareas[numero_tarea]['completada'] = True
            guardar_tareas(tareas)
            label_info.config(text=f"Tarea #{numero_tarea + 1} completada.")
            ajustar_tamaño_texto()
            speak(f"Tarea #{numero_tarea + 1} completada.")
            return
        else:
            if tareas[numero_tarea]['completada']:
                label_info.config(text="Número de tarea ya completada.")
                ajustar_tamaño_texto()
                speak("Número de tarea ya completada.")
            else:
                label_info.config(text="Número de tarea incorrecto.")
                ajustar_tamaño_texto()
                speak("Número de tarea incorrecto.")
    except ValueError:
        label_info.config(text="Error: El número de tarea debe ser un número entero.")
        ajustar_tamaño_texto()
        speak("Error: El número de tarea debe ser un número entero.")

def eliminar_tarea(tareas, query):
    if not tareas:
        label_info.config(text="No tienes tareas pendientes.")
        ajustar_tamaño_texto()
        speak("No tienes tareas pendientes.")
        return
    
    numero_tarea = parsear_numero_elemento(query)
    while not numero_tarea:
        label_info.config(text="Por favor, indica el número de la tarea que quieres eliminar.")
        ajustar_tamaño_texto()
        speak("Por favor, indica el número de la tarea que quieres eliminar.")
        
        text = 'Si no quieres continuar puedes decir "para" o "terminar" para volver al asistente'
        numero_tarea_str = listen(advice_text=text)
        if pattern_detener.search(numero_tarea_str):
            return
        numero_tarea = parsear_numero_elemento(numero_tarea_str)
        if not numero_tarea:
            label_info.config(text="No se detectó ningún número de tarea. Por favor, intenta de nuevo.")
            ajustar_tamaño_texto()
            speak("No se detectó ningún número de tarea. Por favor, intenta de nuevo.")
    
    try:
        numero_tarea = int(numero_tarea) - 1
        if 0 <= numero_tarea < len(tareas):
            label_info.config(text="Estas seguro de borrar esta tarea?")
            ajustar_tamaño_texto()
            speak("Estas seguro de borrar esta tarea?")
            descripcion = tareas[numero_tarea]['descripcion']
            fecha_limite_str = tareas[numero_tarea]['fecha_limite'].strftime('%d-%m-%Y') if tareas[numero_tarea]['fecha_limite'] else "Sin fecha límite"
            estado = "Completada" if tareas[numero_tarea].get('completada', False) else "Pendiente"
            label_info.config(text=f"{numero_tarea}. {descripcion}")
            ajustar_tamaño_texto()
            speak(f"{numero_tarea}. {descripcion}")
            label_info.config(text=f"Fecha límite: {fecha_limite_str} - Estado: {estado}")
            ajustar_tamaño_texto()
            speak(f"Fecha límite: {fecha_limite_str} - Estado: {estado}")
            
            text = 'Di "si" para borrar esta tarea'
            respuesta = listen(advice_text=text)
            if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
                return
            del tareas[numero_tarea]
            guardar_tareas(tareas)
            label_info.config(text=f"Tarea #{numero_tarea + 1} eliminada.")
            ajustar_tamaño_texto()
            speak(f"Tarea #{numero_tarea + 1} eliminada.")
            return
        else:
            label_info.config(text="Número de tarea incorrecto.")
            ajustar_tamaño_texto()
            speak("Número de tarea incorrecto.")
    except ValueError:
        label_info.config(text="Error: El número de tarea debe ser un número entero.")
        ajustar_tamaño_texto()
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
    label_info.config(text="Por favor, graba la nota de voz.")
    ajustar_tamaño_texto()
    speak("Por favor, graba la nota de voz.")
    while not nota_voz:
        label_info.config(text="Grabando...")
        ajustar_tamaño_texto()
        
        nota_voz = listen(tiempo_minimo=5, tiempo_maximo=60)
        if not nota_voz:
            label_info.config(text="No se detectó ninguna nota de voz. ¿Quieres intentarlo de nuevo?")
            ajustar_tamaño_texto()
            speak("No se detectó ninguna nota de voz. ¿Quieres intentarlo de nuevo?")
            
            text = 'Di "si" para intentarlo otra vez.'
            respuesta = listen(advice_text=text)
            if respuesta.lower() in ["sí", "si"]:
                label_info.config(text="Grabando la nota de voz otra vez.")
                ajustar_tamaño_texto()
                speak("Grabando la nota de voz otra vez.")
            else:
                return
        else:
            label_info.config(text="Es esta la nota de voz que quieres guardar?")
            ajustar_tamaño_texto()
            speak("Es esta la nota de voz que quieres guardar?")
            label_info.config(text=nota_voz)
            ajustar_tamaño_texto()
            speak(nota_voz)
            
            text = 'Di "si" para guardar la nota de voz'
            respuesta = listen(advice_text=text)
            if not re.compile(r"\b(sí|si)\b", re.IGNORECASE).search(respuesta):
                nota_voz = None

    notas.append(nota_voz)
    guardar_notas(notas)
    label_info.config(text="Nota de voz guardada.")
    ajustar_tamaño_texto()
    speak("Nota de voz guardada.")

def reproducir_nota(notas, query):
    if not notas:
        label_info.config(text="No tienes notas de voz guardadas.")
        ajustar_tamaño_texto()
        speak("No tienes notas de voz guardadas.")
        return
    
    numero_nota = parsear_numero_elemento(query)
    while not numero_nota:
        label_info.config(text="Por favor, indica el número de la nota que quieres reproducir.")
        ajustar_tamaño_texto()
        speak("Por favor, indica el número de la nota que quieres reproducir.")
        
        text = 'Si no quieres continuar puedes decir "detente" o "terminar" para volver al asistente'
        numero_nota_str = listen(advice_text=text)
        if pattern_detener.search(numero_nota_str):
            return
        numero_nota = parsear_numero_elemento(numero_nota_str)
        if not numero_nota:
            label_info.config(text="No se pudo entender el número de la nota. Por favor, intenta de nuevo.")
            ajustar_tamaño_texto()
            speak("No se pudo entender el número de la nota. Por favor, intenta de nuevo.")

    try:
        numero_nota = int(numero_nota) - 1
        if 0 <= numero_nota < len(notas):
            label_info.config(text=f"Reproduciendo nota: {notas[numero_nota]}.")
            ajustar_tamaño_texto()
            speak(f"Reproduciendo nota: {notas[numero_nota]}.")
        else:
            label_info.config(text="Número de nota incorrecto.")
            ajustar_tamaño_texto()
            speak("Número de nota incorrecto.")
    except ValueError:
        label_info.config(text="Error: El número de nota debe ser un número entero.")
        ajustar_tamaño_texto()
        speak("Error: El número de nota debe ser un número entero.")

def eliminar_nota(notas, query):
    if not notas:
        label_info.config(text="No tienes notas de voz guardadas.")
        ajustar_tamaño_texto()
        speak("No tienes notas de voz guardadas.")
        return
    
    numero_nota = parsear_numero_elemento(query)
    while not numero_nota:
        label_info.config(text="Por favor, indica el número de la nota que quieres eliminar.")
        ajustar_tamaño_texto()
        speak("Por favor, indica el número de la nota que quieres eliminar.")
        
        text = 'Si no quieres continuar puedes decir "para" o "basta" para volver al asistente'
        numero_nota_str = listen(advice_text=text)
        if pattern_detener.search(numero_nota_str):
            return
        numero_nota = parsear_numero_elemento(numero_nota_str)
        if not numero_nota:
            label_info.config(text="No se pudo entender el número de la nota. Por favor, intenta de nuevo.")
            ajustar_tamaño_texto()
            speak("No se pudo entender el número de la nota. Por favor, intenta de nuevo.")

    try:
        numero_nota = int(numero_nota) - 1
        if 0 <= numero_nota < len(notas):
            del notas[numero_nota]
            guardar_notas(notas)
            label_info.config(text=f"Nota {numero_nota+1} eliminada.")
            ajustar_tamaño_texto()
            speak(f"Nota {numero_nota+1} eliminada.")
        else:
            label_info.config(text="Número de nota incorrecto.")
            ajustar_tamaño_texto()
            speak("Número de nota incorrecto.")
    except ValueError:
        label_info.config(text="Error: El número de nota debe ser un número entero.")
        ajustar_tamaño_texto()
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

def hora():
    hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
    speak(f"La hora actual es {hora_actual}.")
    return

def configurar_alarma(query):
    hora_alarma = parsear_hora(query)
    while not hora_alarma:
        label_info.config(text="Por favor, indica la hora para configurar la alarma.")
        ajustar_tamaño_texto()
        speak("Por favor, indica la hora para configurar la alarma.")
        
        text = 'Si no quieres continuar puedes decir "salir" o "atras" para volver al asistente'
        hora_alarma_str = listen(advice_text=text)
        if pattern_detener.search(hora_alarma_str):
            return
        hora_alarma = parsear_hora(hora_alarma_str)
        if not hora_alarma:
            label_info.config(text="No se pudo entender la hora. Por favor, intenta de nuevo.")
            ajustar_tamaño_texto()
            speak("No se pudo entender la hora. Por favor, intenta de nuevo.")
    
    label_info.config(text=f"Alarma: {hora_alarma.strftime('%I:%M %p')}")
    ajustar_tamaño_texto()
    speak(f"Alarma configurada para las {hora_alarma.strftime('%I:%M %p')}.")
    tiempo_alarma = calcular_tiempo_alarma(hora_alarma)
    alarma_thread = threading.Thread(target=esperar_alarma, args=(tiempo_alarma,))
    alarma_thread.start()
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
    global activacion
    
    # Configurar la etiqueta de información en la zona superior derecha de la pantalla
    label_alarma = tk.Label(root, text="00:00:00", font=("Arial", 30), anchor='n')
    label_alarma.pack(side=tk.TOP, anchor=tk.NE)  # Coloca la etiqueta en la esquina superior derecha
        
    # Actualizar la etiqueta con el tiempo de la alarma
    label_alarma.config(text=tiempo_alarma.strftime("%H:%M"))
    label_alarma.update()
    
    tiempo_restante = tiempo_alarma - datetime.datetime.now()
    segundos_restantes = tiempo_restante.total_seconds()
    time.sleep(segundos_restantes)
    
    # Destruir el marco vacío y la etiqueta al finalizar la alarma
    label_alarma.destroy()
    
    # Activar la alarma
    alarma_activada = True
    activacion = True

def configurar_temporizador(query):
    duracion = parsear_duracion(query)
    while not duracion:
        label_info.config(text="Por favor, indica la duración para configurar el temporizador.")
        ajustar_tamaño_texto()
        speak("Por favor, indica la duración para configurar el temporizador.")
        
        text = 'Si no quieres continuar puedes decir "basta" o "detente" para volver al asistente'
        duracion_str = listen(advice_text=text)
        if pattern_detener.search(duracion_str):
            return
        duracion = parsear_duracion(duracion_str)
        if not duracion:
            label_info.config(text="No se pudo entender la duración. Por favor, intenta de nuevo.")
            ajustar_tamaño_texto()
            speak("No se pudo entender la duración. Por favor, intenta de nuevo.")
    
    label_info.config(text=f"Temporizador configurado para {duracion} segundos.")
    ajustar_tamaño_texto()
    speak(f"Temporizador configurado para {duracion} segundos.")
    temporizador_thread = threading.Thread(target=esperar_temporizador, args=(duracion,))
    temporizador_thread.start()
    return

def esperar_temporizador(duracion_segundos):
    global alarma_activada
    global activacion
    
    # Configurar la etiqueta de información en la zona superior derecha de la pantalla
    label_temporizador = tk.Label(root, text="00:00:00", font=("Arial", 30))
    label_temporizador.pack(side=tk.TOP, fill='x')  # Coloca la etiqueta en la esquina superior
    
    tiempo_restante = duracion_segundos
    
    while tiempo_restante > 0:
        tiempo_horas = tiempo_restante // 3600
        tiempo_minutos = (tiempo_restante % 3600) // 60
        tiempo_segundos = tiempo_restante % 60
        tiempo_formateado = "{:02}:{:02}:{:02}".format(tiempo_horas, tiempo_minutos, tiempo_segundos)
        
        # Actualizar la etiqueta con el tiempo restante
        label_temporizador.config(text=tiempo_formateado)
        label_temporizador.update()
        
        tiempo_restante -= 1
        time.sleep(1)
    
    # Destruir el marco vacío y la etiqueta al finalizar el temporizador
    label_temporizador.destroy()
    
    # Activar la alarma
    alarma_activada = True
    activacion = True
    
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
        label_info.config(text="Por favor, indica el número para configurar el contador.")
        ajustar_tamaño_texto()
        speak("Por favor, indica el número para configurar el contador.")
        
        text = 'Si no quieres continuar puedes decir "para" o "salir" para volver al asistente'
        numero_str = listen(advice_text=text)
        if pattern_detener.search(numero_str):
            return
        numero = parsear_numero(numero_str)
        if not numero:
            label_info.config(text="No se pudo entender el número. Por favor, intenta de nuevo.")
            ajustar_tamaño_texto()
            speak("No se pudo entender el número. Por favor, intenta de nuevo.")
    
    
    label_info.config(text=f"Contando hasta {numero}.")
    ajustar_tamaño_texto()
    speak(f"Contando hasta {numero}.")
    for i in range(numero-1):
        label_info.config(text=f"{i+1}")
        ajustar_tamaño_texto()
        speak(f"{i+1}!")
        time.sleep(1)
    label_info.config(text=f"¡{numero}!")
    ajustar_tamaño_texto()
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
    
def terapia():
    label_info.config(text="")
    while True:
        load_and_show_image(os.path.join('init', "menu.png"))
        speak("Por favor, escoge entre jugar y recordar.")
        terapia = None
        while not terapia:
            text = 'Puedes decir "atras" o "retroceder" para volver al asistente'
            terapia_str = listen(advice_text=text)
            if pattern_detener.search(terapia_str):
                return
            terapia = parsear_terapia(terapia_str)
            
        if terapia == 1:
            juego()
        elif terapia == 2:
            remember()
            
    load_and_show_image(None)

def parsear_terapia(terapia):
    if pattern_juegos.search(terapia):
        return 1   
    elif pattern_remember.search(terapia):
        return 2
    else:
        return None
    
def juego():
    while True:
        load_and_show_image(os.path.join('ejercicios', "menu_juegos.png"))
        speak("Por favor, escoge entre atencion focal, busqueda visual y concentracion.")
        juego = None
        while not juego:
            text = 'Puedes decir "atras" o "retroceder" para volver al menu anterior'
            juego_str = listen(advice_text=text)
            if pattern_detener.search(juego_str):
                return
            juego = parsear_juego(juego_str)
        
        if terapia == 1:
            juego_af()
        elif terapia == 2:
            juego_bv()
        elif terapia == 3:
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
    directorio = os.path.join('ejercicios', 'Atencion_focal')
    ruta_directorio = os.path.abspath(directorio)
    patrones = ['*.png']
    ex = []
    for patron in patrones:
        ex.extend(glob.glob(os.path.join(ruta_directorio, patron)))   
    for n, exercices in enumerate(ex):
        #Habria que poner un tutorial de como funcionan los juegos
        load_and_show_image(os.path.join('', exercices))
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
    
def juego_bv():
    directorio = os.path.join('ejercicios', 'Busqueda_visual')
    ruta_directorio = os.path.abspath(directorio)
    patrones = ['*.png']
    ex = []
    for patron in patrones:
        ex.extend(glob.glob(os.path.join(ruta_directorio, patron)))   
    for n, exercices in enumerate(ex):
        #Habria que poner un tutorial de como funcionan los juegos
        load_and_show_image(os.path.join('', exercices))
        speak("Encuentra la figura que es igual a la del circulo de entre todas estas")
        acertado = False
        while not acertado:
            query = listen(tiempo_minimo=3, tiempo_maximo=3)
            if n == 0:
                if (re.compile(r"\b(cinco|5)\b", re.IGNORECASE)).search(query):
                    speak("¡Muy bien! Has acertado. A por el siguiente.")
                    time.sleep(2)
                    acertado = True
                    break
                elif (re.compile(r"\b(uno|dos|tres|cuatro|seis|siete|ocho|nueve|diez|once|doce|1|2|3|4|6|7|8|9|10|11|12)\b", re.IGNORECASE)).search(query):
                    speak("Ups. Me parece que es incorrecto.")
                    time.sleep(3)
                else:
                    speak("Lo siento. No te he entendido.")
                    time.sleep(1)
            if n == 1:
                if (re.compile(r"\b(once|11)\b", re.IGNORECASE)).search(query):
                    speak("¡Muy bien! Has acertado. A por el siguiente.")
                    time.sleep(2)
                    acertado = True
                    break
                elif (re.compile(r"\b(uno|dos|tres|cuatro|seis|siete|ocho|nueve|diez|cinco|doce|1|2|3|4|6|7|8|9|10|5|12)\b", re.IGNORECASE)).search(query):
                    speak("Ups. Me parece que es incorrecto.")
                    time.sleep(3)
                else:
                    speak("Lo siento. No te he entendido.")
                    time.sleep(1)
            if n == 2:
                if (re.compile(r"\b(ocho|8)\b", re.IGNORECASE)).search(query):
                    speak("¡Muy bien! Has acertado. A por el siguiente.")
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
                    speak("¡Muy bien! Has acertado.")
                    time.sleep(2)
                    acertado = True
                    break
                elif (re.compile(r"\b(uno|dos|tres|cuatro|seis|siete|ocho|cinco|diez|once|doce|1|2|3|4|6|7|8|5|10|11|12)\b", re.IGNORECASE)).search(query):
                    speak("Ups. Me parece que es incorrecto.")
                    time.sleep(3)
                else:
                    speak("Lo siento. No te he entendido.")
                    time.sleep(1)

def juego_c():
    directorio = os.path.join('ejercicios', 'Concentracion')
    ruta_directorio = os.path.abspath(directorio)
    patrones = ['*.png']
    ex = []
    for patron in patrones:
        ex.extend(glob.glob(os.path.join(ruta_directorio, patron)))   
    for n, exercices in enumerate(ex):
        #Habria que poner un tutorial de como funcionan los juegos
        load_and_show_image(os.path.join('', exercices))
        speak("Encuentra la figura que es igual a la del circulo de entre todas estas")
        acertado = False
        while not acertado:
            query = listen(tiempo_minimo=3, tiempo_maximo=3)
            if n == 0:
                if (re.compile(r"\b(cinco|5)\b", re.IGNORECASE)).search(query):
                    speak("¡Muy bien! Has acertado. A por el siguiente.")
                    time.sleep(2)
                    acertado = True
                    break
                elif (re.compile(r"\b(uno|dos|tres|cuatro|seis|siete|ocho|nueve|diez|once|doce|1|2|3|4|6|7|8|9|10|11|12)\b", re.IGNORECASE)).search(query):
                    speak("Ups. Me parece que es incorrecto.")
                    time.sleep(3)
                else:
                    speak("Lo siento. No te he entendido.")
                    time.sleep(1)
            if n == 1:
                if (re.compile(r"\b(once|11)\b", re.IGNORECASE)).search(query):
                    speak("¡Muy bien! Has acertado. A por el siguiente.")
                    time.sleep(2)
                    acertado = True
                    break
                elif (re.compile(r"\b(uno|dos|tres|cuatro|seis|siete|ocho|nueve|diez|cinco|doce|1|2|3|4|6|7|8|9|10|5|12)\b", re.IGNORECASE)).search(query):
                    speak("Ups. Me parece que es incorrecto.")
                    time.sleep(3)
                else:
                    speak("Lo siento. No te he entendido.")
                    time.sleep(1)
            if n == 2:
                if (re.compile(r"\b(ocho|8)\b", re.IGNORECASE)).search(query):
                    speak("¡Muy bien! Has acertado. A por el siguiente.")
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
                    speak("¡Muy bien! Has acertado.")
                    time.sleep(2)
                    acertado = True
                    break
                elif (re.compile(r"\b(uno|dos|tres|cuatro|seis|siete|ocho|cinco|diez|once|doce|1|2|3|4|6|7|8|5|10|11|12)\b", re.IGNORECASE)).search(query):
                    speak("Ups. Me parece que es incorrecto.")
                    time.sleep(3)
                else:
                    speak("Lo siento. No te he entendido.")
                    time.sleep(1)

def remember():
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
    
    - Terapia: ¡También puedo entretenerte con algunos juegos o hacerte recordar!
    
    - Cambiar fondo: Para elegir un color de fondo entre blanco, gris y negro, di "cambiar fondo"
    
    - Ayuda: Siempre puedes pedir ayuda diciendo "ayuda" o "ayúdame por favor".
    
    ¡Espero que encuentres útiles estas opciones! ¿En qué puedo ayudarte hoy?
    """
    print(mensaje)
    label_info.config(text=mensaje)
    ajustar_tamaño_texto()
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

def listen(tiempo_minimo=3, tiempo_maximo=10, advice_text=None):
    global activacion
    global alarma_activada
    
    try:
        eliminar = False
        if activacion:
            # Dibujar la franja azul que ocupe todo el ancho
            franja = canvas.create_rectangle(0, 0, root.winfo_screenwidth(), 30, outline="")
            canvas.itemconfig(franja, fill="cyan")
            eliminar = True
            
        if advice_text:
            advice_label.config(text=advice_text)
            advice_label.update()
        
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
        
        if advice_text:
            advice_label.config(text="")
            advice_label.update()
        
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


pattern_activacion = re.compile(r"\b(paco|opaco|pago|bajo|macho|banco)\b", re.IGNORECASE)

def main_loop():
    agenda = cargar_agenda()
    tareas = cargar_tareas()
    notas = cargar_notas()
    
    global alarma_activada
    alarma_activada = False
    
    global activacion
    activacion = False
    
    global detener
    detener = False
    
    # Carga la imagen inicial
    load_and_show_image(os.path.join('init', "black.png"))
    load_and_play_audio(os.path.join('audios', "encendido.mp3"))
    load_and_show_image(os.path.join('init', "black_logo.png"))
    time.sleep(2)
    load_and_show_image(None)
    
    while not detener:
        if not alarma_activada:
            hora_actual = datetime.datetime.now().strftime("%H:%M")
            label_info.config(text=f"{hora_actual}")
            ajustar_tamaño_texto()

            random_advice = random.choice(advice_list)
            query = listen(tiempo_minimo=3, tiempo_maximo=10, advice_text=random_advice)
        
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
                    hora()
                elif pattern_configurar_alarma.search(query):
                    configurar_alarma(query)
                elif pattern_configurar_temporizador.search(query):
                    configurar_temporizador(query)
                elif pattern_configurar_contador.search(query):
                    configurar_contador(query)
                    
                # Juegos y terapia
                elif pattern_terapia.search(query):
                    terapia()
    
                # Despedida
                elif pattern_despedida.search(query):
                    label_info.config(text="¡Hasta luego! Que tengas un buen día.")
                    ajustar_tamaño_texto()
                    speak("¡Hasta luego! Que tengas un buen día.")
    
                # Ayuda
                elif pattern_ayuda.search(query):
                    ayuda()
                    continue
                    
                # Procesamiento de consultas generales
                elif pattern_saludo.search(query):
                    label_info.config(text="¡Hola! ¿En qué puedo ayudarte?")
                    ajustar_tamaño_texto()
                    speak("¡Hola! ¿En qué puedo ayudarte?")
                    continue
                
                # Configuracion del sistema
                elif pattern_cambiar_color.search(query):
                    cambiar_color(query)
                
                else:
                    label_info.config(text="Lo siento, no entendí eso.")
                    ajustar_tamaño_texto()
                    speak("Lo siento, no entendí eso.") 
                
                activacion = False
                
            elif pattern_activacion.search(query):
                label_info.config(text="En qué puedo ayudarte?")
                ajustar_tamaño_texto()
                speak("¿En qué puedo ayudarte?")
                activacion = True
        else:
            speak("¡Alarma!")
            time.sleep(0.5)
            speak("¡Alarma!")
            time.sleep(0.5)
            speak("¡Alarma!")
            time.sleep(0.5)
            # Aquí podría agregar la reproducción de un sonido de alarma o cualquier otra acción que desee.
            text = 'Di "para" o "detener" para detener la alarma'
            parar = listen(tiempo_minimo=2, tiempo_maximo=2, advice_text=text)
            if pattern_detener.search(parar):
                speak("Alarma detenida.")
                alarma_activada = False
                activacion = False
"""
def detener_programa():
    global detener
    detener = True
    
    root.quit()  # Detener el bucle principal de Tkinter
    root.destroy()  # Cierra la ventana principal
    if main_thread and main_thread.is_alive():
        main_thread.join()  # Espera a que el hilo principal termine antes de salir
    sys.exit()  # Sale del programa por completo
"""
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
    
def cambiar_color(query):
    color_fondo, color_texto = parsear_color(query)
    while not color_fondo and not color_texto:
        label_info.config(text="Por favor, escoge entre los colores blanco, gris y negro.")
        ajustar_tamaño_texto()
        speak("Por favor, escoge entre los colores blanco, gris y negro.")
        
        color_str = listen()
        if pattern_detener.search(color_str):
            return
        color_fondo, color_texto = parsear_color(color_str)
        if not color_fondo and not color_texto:
            label_info.config(text="No se pudo entender el color. Por favor, intenta de nuevo.")
            ajustar_tamaño_texto()
            speak("No se pudo entender el color. Por favor, intenta de nuevo.")
    
    root.configure(bg=color_fondo)
    
    label_info.configure(bg=color_fondo)
    label_info.configure(fg=color_texto)
    
    advice_label.configure(bg=color_fondo)
    advice_label.configure(fg=color_texto)

def parsear_color(color):
    # Expresión regular para extraer el color
    patron_color = re.compile(r"\b(blanco|claro|gris|opaco|negro|oscuro)\b", re.IGNORECASE)
    match = patron_color.search(color)
    if match:
        # Comprobar los grupos de coincidencia para obtener el color correcto
        for grupo in match.groups():
            if grupo:
                if re.search(r"\b(blanco|claro)\b", grupo, re.IGNORECASE):
                    return "white", "black"
                elif re.search(r"\b(gris|opaco)\b", grupo, re.IGNORECASE):
                    return "gray", "white"
                elif re.search(r"\b(negro|oscuro)\b", grupo, re.IGNORECASE):
                    return "black", "white"          
    return None, None

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

# Crear el widget Label con texto
label_info = tk.Label(root, text="", font=("Arial", 50), justify="center", anchor="center")
label_info.pack(expand=True, fill='both')

letras_por_linea = calcular_letras_por_linea(label_info)
lineas_por_pantalla = calcular_lineas_por_pantalla(label_info)

# Crear un lienzo (canvas) y hacer que ocupe todo el ancho
canvas = tk.Canvas(label_info, height=30)
canvas.pack(side="bottom", fill="x")

# Configuración del texto en la esquina inferior derecha
advice_label = tk.Label(root, text="", font=("Arial", 20), justify="center", anchor="center")
advice_label.place(relx=0.05, rely=0.90)

# Lista de consejos
advice_list = [
    'Saludos: Puedes saludarme diciendo "Hola", "Buenos días", "Buenas tardes" o "Buenas noches".',
    'Consultar la hora: Simplemente menciona "hora" y te diré la hora actual',
    'Consultar eventos: Di "consultar eventos" para ver los eventos agendados para hoy.',
    'Agregar evento: Di "agregar evento" para añadir un nuevo evento a tu agenda.',
    'Modificar evento: Si necesitas hacer cambios de horario a un evento existente, di "modificar evento".',
    'Eliminar evento: Di "eliminar evento" para borrar un evento de tu agenda.',
    'Mostrar tareas: Para ver tus tareas pendientes, di "mostrar tareas".',
    'Agregar tarea: Para añadir una nueva tarea a tu lista, di "agregar tarea".',
    'Marcar tarea como completada: Si has completado una tarea, di "marcar tarea como completada".',
    'Eliminar tarea: Si deseas borrar una tarea de tu lista, di "eliminar tarea".',
    'Agregar nota: Puedes guardar notas de voz diciendo "agregar nota".',
    'Reproducir nota: Si quieres escuchar tus notas guardadas, di "reproducir nota".',
    'Eliminar nota: Para eliminar una nota, simplemente di "eliminar nota".',
    'Configurar alarma: Si necesitas una alarma, di "alarma".',
    'Configurar temporizador: Para establecer un temporizador, di "temporizador".',
    'Configurar contador: Para establecer un contador, di "cuenta"',
    'Terapia: ¡También puedo entretenerte con algunos juegos o hacerte recordar!',
    'Cambiar fondo: Para elegir un color de fondo entre blanco, gris y negro, di "cambiar fondo"',
    'Ayuda: Siempre puedes pedir ayuda diciendo "ayuda" o "ayúdame por favor".'
]

# Botón para detener el programa
#btn_detener = tk.Button(root, text="Detener programa", command=detener_programa)
#btn_detener.pack(side=tk.TOP, anchor=tk.NE)  # Coloca el botón en la esquina superior derecha

# Ejecutar el bucle principal en un hilo aparte
main_thread = threading.Thread(target=main_loop)
main_thread.start()

# Ejecutar la aplicación
root.mainloop()