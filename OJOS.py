from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import Image
import time
# Configurar la pantalla
serial1 = i2c(port=1, address=0x3C)  
device1 = ssd1306(serial1)

serial2 = i2c(port=3, address=0x3C)  
device2 = ssd1306(serial2)
screen_width = 128
screen_height = 64

# Cargar las imágenes
ojo1 = Image.open('ojo1.png').convert('1').resize((screen_width, screen_height)).transpose(Image.FLIP_LEFT_RIGHT)
ojo2 = Image.open('ojo2.png').convert('1').resize((screen_width, screen_height)).transpose(Image.FLIP_LEFT_RIGHT)
ojo3 = Image.open('ojo3.png').convert('1').resize((screen_width, screen_height)).transpose(Image.FLIP_LEFT_RIGHT)
ojo4 = Image.open('ojo4.png').convert('1').resize((screen_width, screen_height)).transpose(Image.FLIP_LEFT_RIGHT)
ojo5 = Image.open('ojo5.png').convert('1').resize((screen_width, screen_height)).transpose(Image.FLIP_LEFT_RIGHT)



# Función para mostrar una imagen en la pantalla
def show_image(device, image):
    with canvas(device) as draw:
        draw.bitmap((0, 0), image, fill="white")

# Animación de ojos
while True:
    show_image(device1, ojo1)
    show_image(device2, ojo1)
    time.sleep(5)
    show_image(device1, ojo1)
    show_image(device2, ojo2)
    time.sleep(0.01)
    show_image(device1, ojo1)
    show_image(device2, ojo1)
    time.sleep(5)
    show_image(device1, ojo2)
    show_image(device2, ojo2)
    time.sleep(0.01)
    show_image(device1, ojo3)
    show_image(device2, ojo3)
    time.sleep(0.01)
    show_image(device1, ojo4)
    show_image(device2, ojo4)
    time.sleep(0.01)
    show_image(device1, ojo5)
    show_image(device2, ojo5)
    time.sleep(0.01)
    show_image(device1, ojo4)
    show_image(device2, ojo4)
    time.sleep(0.01)
    show_image(device1, ojo3)
    show_image(device2, ojo3)
    time.sleep(0.01)
    show_image(device1, ojo2)
    show_image(device2, ojo2)
    time.sleep(0.01)
    show_image(device1, ojo1)
    show_image(device2, ojo1)
    time.sleep(5)
    show_image(device1, ojo2)
    show_image(device2, ojo2)
    time.sleep(0.01)
    show_image(device1, ojo3)
    show_image(device2, ojo3)
    time.sleep(0.01)
    show_image(device1, ojo4)
    show_image(device2, ojo4)
    time.sleep(0.01)
    show_image(device1, ojo5)
    show_image(device2, ojo5)
    time.sleep(0.01)
    show_image(device1, ojo4)
    show_image(device2, ojo4)
    time.sleep(0.01)
    show_image(device1, ojo3)
    show_image(device2, ojo3)
    time.sleep(0.01)
    show_image(device1, ojo2)
    show_image(device2, ojo2)
    time.sleep(0.01)
