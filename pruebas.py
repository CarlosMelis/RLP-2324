import cv2

def verificar_camara():
    cap = cv2.VideoCapture(0)  # Intenta abrir la cámara en el dispositivo 0

    if not cap.isOpened():
        print("No se pudo abrir la cámara")
        return

    ret, frame = cap.read()

    if ret:
        cv2.imshow('Frame', frame)
        cv2.waitKey(0)  # Espera a que se presione una tecla para cerrar la ventana
    else:
        print("No se pudo capturar una imagen")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    verificar_camara()
