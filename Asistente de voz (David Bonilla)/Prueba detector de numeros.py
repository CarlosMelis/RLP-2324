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

# Ejemplo de uso:

print("Primer texto")
texto = "ciento cuarenta y cuatro mil doscientos treinta y dos"
texto_numeros = convertir_numeros(texto)
print("Texto original:", texto)
print("Texto con números:", texto_numeros)
print("Texto correcto:   ", 144232)

print("Segundo texto")
texto = "ciento cuarenta y cuatro mil doscientos treinta y dos millones quinientos"
texto_numeros = convertir_numeros(texto)
print("Texto original:", texto)
print("Texto con números:", texto_numeros)
print("Texto correcto:   ", 144232000500)

print("Tercer texto")
texto = "ciento cuarenta y cuatro mil doscientos treinta y dos millones quinientos mil trescientos veintiocho"
texto_numeros = convertir_numeros(texto)
print("Texto original:", texto)
print("Texto con números:", texto_numeros)
print("Texto correcto:   ", 144232500328)

print("Cuarto texto")
texto = "doscientos mil quinientos millones cien mil cien"
texto_numeros = convertir_numeros(texto)
print("Texto original:", texto)
print("Texto con números:", texto_numeros)
print("Texto correcto:   ", 200500100100)

print("Cuarto texto")
texto = "hola buenos dias doscientos mil quinientos millones cien mil cien que pases un buen fin de semana"
texto_numeros = convertir_numeros(texto)
print("Texto original:", texto)
print("Texto con números:", texto_numeros)
print("Texto correcto:   ", 200500100100)

print("Cuarto texto")
texto = "Pon la alarma para dentro de cinco mil cien segundos"
texto_numeros = convertir_numeros(texto)
print("Texto original:", texto)
print("Texto con números:", texto_numeros)
print("Texto correcto:   ", 5100)