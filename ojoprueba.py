from smbus2 import SMBus
import time

# Direcciones I2C de las pantallas
OLED_1_ADDR = 0x3C  # Dirección de la primera pantalla en bus 1
OLED_2_ADDR = 0x3C  # Dirección de la segunda pantalla en bus 3 (misma dirección pero en diferente bus)

# Inicializar el bus I2C principal (bus 1)
bus1 = SMBus(1)
# Inicializar el segundo bus I2C (bus 3)
bus3 = SMBus(3)

def initialize_oled(bus, address):
    # Aquí deberías poner los comandos necesarios para inicializar la pantalla OLED
    # Por ejemplo, encender la pantalla, configurar el modo de visualización, etc.
    # Este es solo un ejemplo genérico
    bus.write_byte_data(address, 0x00, 0xAE)  # Apagar la pantalla
    time.sleep(0.1)
    bus.write_byte_data(address, 0x00, 0xAF)  # Encender la pantalla
    time.sleep(0.1)

# Inicializar ambas pantallas
initialize_oled(bus1, OLED_1_ADDR)
initialize_oled(bus3, OLED_2_ADDR)

# Ejemplo de escritura en la primera pantalla
bus1.write_byte_data(OLED_1_ADDR, 0x00, 0xAF)  # Comando para encender la pantalla

# Ejemplo de escritura en la segunda pantalla
bus3.write_byte_data(OLED_2_ADDR, 0x00, 0xAF)  # Comando para encender la pantalla

# No olvides cerrar los buses al final
bus1.close()
bus3.close()