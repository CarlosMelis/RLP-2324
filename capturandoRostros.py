import cv2
import os
import imutils
import numpy as np
import time

def speak(text):
    os.system(f'echo "{text}" | festival --tts --language spanish')

def capturando_rostros():
    global most_detected_unknown
    most_detected_unknown = None
    ## CONFIGURACIÓN DE RUTAS ##
    currentPath = os.getcwd()  # Obtiene la ruta del directorio actual
    dataPath = os.path.join(currentPath, 'Data')  # Construye la ruta a la carpeta 'Data' en el directorio actual
    
    if not os.path.exists(dataPath):
        os.makedirs(dataPath)
        print(f"Directorio {dataPath} creado")
    else:
        print(f"Directorio {dataPath} ya existe")
    
    face_recognizer = cv2.face.EigenFaceRecognizer_create()
    faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Verificar si hay un modelo entrenado
    if os.path.exists('modeloEigenFace.xml'):
        face_recognizer.read('modeloEigenFace.xml')
        imagePaths = os.listdir(dataPath)
        print("Modelo existente cargado")
    else:
        imagePaths = []
        print("No se encontró modelo existente, se creará uno nuevo")
    
    cap = cv2.VideoCapture(0)
    
    count = 0
    person_captured = False
    start_time = time.time()
    unknown_counter = 0
    unknown_threshold = 15  # Número de frames consecutivos para confirmar rostro desconocido
    recognized_counts = {}

    while not person_captured and (time.time() - start_time) < 10:
        ret, frame = cap.read()
        if not ret: 
            print("No se pudo capturar la imagen de la cámara")
            break
    
        frame = imutils.resize(frame, width=640)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        auxFrame = frame.copy()
    
        faces = faceClassif.detectMultiScale(gray, 1.3, 5)
    
        for (x, y, w, h) in faces:
            rostro = auxFrame[y:y+h, x:x+w]
            rostro_resized = cv2.resize(rostro, (150, 150), interpolation=cv2.INTER_CUBIC)
            
            # Verificar si el rostro ya está en la base de datos
            if imagePaths:
                result = face_recognizer.predict(cv2.cvtColor(rostro_resized, cv2.COLOR_BGR2GRAY))
                if result[1] < 5700:
                    persona_reconocida = imagePaths[result[0]]
                    print("Persona reconocida:", persona_reconocida)
                    unknown_counter = 0
                    
                    # Contar la persona reconocida
                    if persona_reconocida in recognized_counts:
                        recognized_counts[persona_reconocida] += 1
                    else:
                        recognized_counts[persona_reconocida] = 1
                    
                    unknown_counter = 0
                else:
                    print("Persona desconocida")
                    unknown_counter += 1

                    # Si se ha confirmado que es una persona desconocida
                    if unknown_counter >= unknown_threshold:
                        # Crear carpeta para el rostro desconocido
                        person_count = len([name for name in os.listdir(dataPath) if name.startswith('Desconocido_')]) + 1
                        unknown_faces_path = os.path.join(dataPath, f'Desconocido_{person_count}')
                        if not os.path.exists(unknown_faces_path):
                            os.makedirs(unknown_faces_path)
                            print(f"Directorio {unknown_faces_path} creado")
                        
                        # Guardar el rostro desconocido
                        for _ in range(50):
                            cv2.imwrite(os.path.join(unknown_faces_path, 'rostro_{}.jpg'.format(count)), rostro_resized)
                            count += 1
                            ret, frame = cap.read()
                            if not ret:
                                break
                            frame = imutils.resize(frame, width=640)
                            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            auxFrame = frame.copy()
                            faces = faceClassif.detectMultiScale(gray, 1.3, 5)
                            for (x, y, w, h) in faces:
                                rostro = auxFrame[y:y+h, x:x+w]
                                rostro_resized = cv2.resize(rostro, (150, 150), interpolation=cv2.INTER_CUBIC)
                        person_captured = True
                        break
    if recognized_counts:
        most_detected_unknown = max(recognized_counts, key=recognized_counts.get)
        speak("Persona detectada. Bienvenido de nuevo " + most_detected_unknown)
    else:
        speak("Persona no detectada, capturando rostros")

    cap.release()
    cv2.destroyAllWindows()
    
    if person_captured:
        speak("Persona no detectada, capturando rostros")
        ## ENTRENANDO ##
        peopleList = os.listdir(dataPath)
        print('Lista de personas: ', peopleList)
        
        labels = []
        facesData = []
        label = 0
        
        for nameDir in peopleList:
            personPath = os.path.join(dataPath, nameDir)
        
            for fileName in os.listdir(personPath):
                labels.append(label)
                face = cv2.imread(os.path.join(personPath, fileName), 0)
                face = cv2.resize(face, (150, 150), interpolation=cv2.INTER_CUBIC)
                facesData.append(face)
            label += 1
        
        # Métodos para entrenar el reconocedor
        face_recognizer = cv2.face.EigenFaceRecognizer_create()
        
        # Entrenando el reconocedor de rostros
        print("Entrenando...")
        face_recognizer.train(facesData, np.array(labels))
        
        # Almacenando el modelo obtenido
        face_recognizer.write('modeloEigenFace.xml')
        print("Modelo almacenado...")
        speak("Modelo entrenado y almacenado")

if __name__ == "__main__":
    capturando_rostros()
