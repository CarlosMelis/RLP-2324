import cv2
import os
import time
from collections import Counter

def reconocimiento_facial(duration=5):
    currentPath = os.getcwd()
    dataPath = os.path.join(currentPath, 'Data')  # Construye la ruta a la carpeta 'Data' en el directorio actual
    imagePaths = os.listdir(dataPath)
    
    face_recognizer = cv2.face.EigenFaceRecognizer_create()
    face_recognizer.read('modeloEigenFace.xml')
    faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    recognized_names = []  # Lista para almacenar los nombres de las personas reconocidas
    end_time = time.time() + duration  # Define el tiempo de finalización

    while time.time() < end_time:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        auxFrame = gray.copy()
    
        faces = faceClassif.detectMultiScale(gray, 1.3, 5)
    
        for (x, y, w, h) in faces:
            rostro = auxFrame[y:y+h, x:x+w]
            rostro = cv2.resize(rostro, (150, 150), interpolation=cv2.INTER_CUBIC)
            result = face_recognizer.predict(rostro)
    
            if result[1] < 5700:
                nombre = imagePaths[result[0]]
                recognized_names.append(nombre)
            else:
                recognized_names.append('Desconocido')
    
    cap.release()

    if recognized_names:
        # Contar la frecuencia de cada nombre y devolver el más común
        most_common_name = Counter(recognized_names).most_common(1)[0][0]
        return most_common_name
    else:
        return 'Ningún rostro reconocido'

# Ejemplo de uso de la función
nombre_reconocido = reconocimiento_facial(duration=5)
print("Nombre reconocido:", nombre_reconocido)
