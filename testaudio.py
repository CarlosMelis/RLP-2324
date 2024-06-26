import glob
import os

directorio = 'ejercicios/Atencion_focal'
ruta_directorio = os.path.abspath(directorio)

# Verifica que la ruta del directorio sea correcta
print("Ruta del directorio:", ruta_directorio)

# Lista todos los archivos .png en el directorio especificado
imagenes = glob.glob(os.path.join(ruta_directorio, '*.png'))

# Muestra los archivos encontrados
print("Archivos encontrados:", imagenes)
