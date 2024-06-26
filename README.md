
# Lopako
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

Lopako es un asistente robot centralizado en la interacción para la estimulación cognitiva de personas que padecen de problemas de memoria (Alzheimer).

## Tabla de contenido

- [Información del proyecto](#información-del-proyecto)
- [Componentes](#componentes)
- [Hardware Scheme](#hardware-scheme)
- [Arquitectura software](#arquitectura-software)
- [Configuración del software](#configuración-del-software)
- [Support](#support)
- [Fotos](#fotos)
- [Video](#video)
- [Autors](#autors)

## Información del proyecto

Este proyecto busca crear un asistente robot completamente enfocado para la estimulación cognitiva con el usuario. Se realizará mediante un asistente de mesa con funcionalidades típicas ya existentes, pero gracias a la inteligencia artificial se podrá interactuar con él a través de voz.

Caracteristicas:
  1. Interacción con modelo de voz o tactil.
  2. Codigo abierto
  3. Facil de comprender
  4. Sin conexión a Internet
  5. Dependencia minima

## Componentes

| [Pantalla](https://eu.robotshop.com/es/products/waveshare-7inch-qled-integrated-display-1024x600-w-dev-accessories?gad_source=1&gclid=CjwKCAjwkuqvBhAQEiwA65XxQPiNJrfmx6yoc__vxjiG-uWRSPLR4n9xQ5F9_rPI3Hyf-9Yth4KZohoC894QAvD_BwE) | [Alimentador 5V Raspberry](https://tienda.bricogeek.com/accesorios-raspberry-pi/813-alimentador-raspberry-pi-3-5v25a.html)     | [Cámara/microfono](https://tienda.bricogeek.com/accesorios-raspberry-pi/822-camara-raspberry-pi-v2-8-megapixels.html)                |
| :-------- | :------- | :------------------------- |
| ![pantalla](https://http2.mlstatic.com/D_NQ_NP_806767-MEC47936666203_102021-O.webp) | ![alimentador](https://github.com/CarlosMelis/RLP-2324/assets/127751829/17632609-ea4e-482d-9030-361675bf979f) | ![cámara](https://m.media-amazon.com/images/I/41JJwg1RrTL.jpg)
| [Raspberry 3B+](https://tienda.bricogeek.com/placas-raspberry-pi/1089-raspberry-pi-3-b-plus.html) | [Pantalla ojos](https://www.amazon.es/AZDelivery-Pantalla-Display-pulgadas-Raspberry/dp/B01L9GC470/ref=sr_1_1?adgrpid=1306220248924282&dib=eyJ2IjoiMSJ9.v19U4AeB3MGCVIraHo-zd81DMAe-f4VgDWpHStVOH89BgQrDf4bhme6maPJvIGCNeCG1GaoJRbVYpyr5GfUfSvEJAf_WR2JKSemZ3i_LQRv3x_pJA4p7EH0kjK0-qPyaWn1fxuU7NJLpdnkicWjlXdU6E5xJAyfjzq5u4bpGPINAhWuAoIk13kKyKhZzJOCSlWas7FcO-nPqc3Yfy17P50oCyBC0CAouNGKvRFtMYN9dc_ekiMh-b-4QLwzoBLwQyNDfwQ-brxwQ1Ejm-kNgs3dICtYXZUUrRIv-40JDt-Q.Ahentau47hHdQZ_CYS5MuWGOoLolvxRVTBVbiLivxtk&dib_tag=se&hvadid=81638854262704&hvbmt=bp&hvdev=c&hvlocphy=3173&hvnetw=o&hvqmt=p&hvtargid=kwd-81639002330313%3Aloc-170&hydadcr=19344_1839968&keywords=pantalla+oled+raspberry&qid=1709760552&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1&smid=A1X7QLRQH87QA3)     | [Servo](https://tienda.bricogeek.com/servomotores/1319-micro-servo-feetech-07kg-fs0403-fb-con-feedback.html)
| ![Raspberry](https://github.com/CarlosMelis/RLP-2324/assets/127751829/2c597496-b605-467a-9c1f-c71f5c0bff2e)| ![Pantalla_ojos](https://ae01.alicdn.com/kf/Sae16499d65714ff984eb4f371cc12b0dz.jpg_640x640Q90.jpg_.webp) | ![Servo](https://www.melopero.com/wp-content/uploads/2019/11/09065-01a.jpg)
| [Speaker](https://www.googleadservices.com/pagead/aclk?sa=L&ai=DChcSEwjVldTS6PiGAxVIQkECHULvA8UYABAGGgJ3cw&gclid=CjwKCAjw-O6zBhASEiwAOHeGxfMZYxY7_doT9o94ubMa0dyn6cSsn6MeCFVIefZ3dusTT5VAMEOrkxoCD_gQAvD_BwE&ohost=www.google.com&cid=CAESVuD2sgzpPO6jDoSzQnzCt7cmS3UVuGRocv2gUJm8DUieSyVRfxu8jw74uzzoRP_c4EIGtmewBOnpixE6Rpee3QWbKV73iqR2kyvbJ7OL_RtpwNwvQFYB&sig=AOD64_2M2JmAhYuQcmkrdhWztXKSCPwKLg&ctype=5&q=&ved=2ahUKEwjArM7S6PiGAxV8SPEDHdRxCWgQ9aACKAB6BAgEEBA&adurl=) | 
| ![Speaker](https://cdn.imprentaonline.net/media/catalog/product/cache/3d885e009f022573916c6c91b73e4325/6/0/6086-001-P_1.webp) | 

## Documentación
Este README solo muestra una parte esencial de este proyecto.
Si está interesado en otros proyectos, visita [Robotics, Language and Planning: RLP Engineering School UAB](https://rlpengineeringschooluab.wordpress.com/) donde encontrará diversos proyectos de robotica de los ultimos años.

## Configuración del software

1. Clonar el repositorio:
```console
foo$bar:~$ git clone https://github.com/CarlosMelis/RLP-2324.git
```

2. Instalar requisitos:
```
foo$bar:~$ pip install -r src/requirements.txt
```

3. Ejecutar main.py

## Hardware Scheme

![Hardware](https://github.com/CarlosMelis/RLP-2324/assets/127751829/7713172f-58f7-409a-bfeb-0575ed978593)


## Arquitectura software

![software](https://github.com/CarlosMelis/RLP-2324/assets/127751829/38d6dd26-ab03-44ba-a06b-1e307ba38100)


## Parte fisica
El robot cuenta con un cuerpo físico impreso en una impresora 3D. El exterior es un amigable robot blanco con una pantalla en el centro, para poder hablar e interactuar con LOPAKO; un agujero donde la cámara analiza el entorno y las personas; unos agujeros para que pase el sonido; una cabeza redonda y grande con unas pantallas como ojos, blancos y movimiento para dar más vida al robot.
<div align="center">
  <img src="https://github.com/CarlosMelis/RLP-2324/assets/127751829/8eed8a4b-0f3d-432e-b03d-4acbbd009055" alt="Pre-gif"/>
</div>

La parte interna del robot cuenta con bastante espacio para dejar la raspberry pi colocada estratégicamente para que cables, altavoz, servo y estructuras de soporte no hagan un lio de cables. 
<div align="center">
  <img src="https://github.com/CarlosMelis/RLP-2324/assets/127751829/839b42e7-304a-4c25-a5a8-8a32a0c56c57" alt="Internal Structure" width="400"/>
</div>

## Software
La parte de software se ha creado con Python, un lenguaje de alto nivel de programación, con la ayuda de librerías públicas como pyaudio, pyttsx3, tkinter o cv2, entre otros. El programa cuenta con funciones para el habla, las imágenes, los juegos, los videos y las funcionalidades que este asistente robótico puede ofrecer. 

El robot cuenta con la funcionalidad de escuchar y responder. Se puede ir moviéndose por la interfaz mediante el habla o mediante el toque de un dedo gracias a la funcionalidad touchpad de la pantalla. 

Para facilitar el entretenimiento de la persona, se han aplicado varios juegos interactivos de atención focal, búsqueda visual y concentración para estimular el cerebro, además de, un video que recuerda los mejores momentos de dicha persona. Cabe recalcar que el video se procesa dependiendo de la persona registrada al momento de encenderse el robot.

La funcionalidad de la cámara es capturar el rostro de la persona y así entrenar un modelo de reconocimiento facial para poder reproducir los diferentes videos que este robot contiene en su base de datos.

## Licencia
MIT

## Aporte
Cualquier aporte es bienvenido!!

## Support

- [Escola d'Enginyeria - UAB Barcelona](https://www.uab.cat/enginyeria/)
- [UAB Open Labs](https://www.uab.cat/open-labs/)

## Autors

- Javier Comes
- David Bonilla
- Carlos Alejandro Melis
- Adrián Gonzalez
