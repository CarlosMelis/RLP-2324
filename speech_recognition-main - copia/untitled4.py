import pygame
import sys

# Inicializa Pygame
pygame.init()

# Configura la ventana
win = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Collage de Imágenes Sincronizadas")

# Carga las imágenes
image_paths = [
    "resources/image1.jpg",
    "resources/image2.jpg",
    "resources/image3.jpg",
    "resources/image4.jpg",
    "resources/image5.jpg"
]
images = [pygame.image.load(path).convert_alpha() for path in image_paths]

# Configura las posiciones iniciales y las velocidades
positions = [(0, 0), (100, 0), (200, 0), (300, 0), (400, 0)]
velocities = [(2, 2)] * len(images)

# Reloj para controlar el framerate
clock = pygame.time.Clock()

# Bucle principal
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Actualiza las posiciones
    for i in range(len(images)):
        positions[i] = (positions[i][0] + velocities[i][0], positions[i][1] + velocities[i][1])

        # Si la imagen alcanza el borde de la ventana, invierte la dirección
        if positions[i][0] <= 0 or positions[i][0] >= win.get_width() - images[i].get_width():
            velocities[i] = (-velocities[i][0], velocities[i][1])
        if positions[i][1] <= 0 or positions[i][1] >= win.get_height() - images[i].get_height():
            velocities[i] = (velocities[i][0], -velocities[i][1])

    # Rellena la ventana con un color de fondo
    win.fill((255, 255, 255))

    # Dibuja las imágenes
    for i in range(len(images)):
        win.blit(images[i], positions[i])

    # Actualiza la pantalla
    pygame.display.flip()

    # Controla el framerate
    clock.tick(60)
