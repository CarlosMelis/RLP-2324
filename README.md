
# Lopako
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

Lopako será un asistente robot centralizado en la interacción para la estimulación cognitiva de personas que padecen de problemas de memoria (Alzheimer).

## Tabla de contenido

- [Información del proyecto]()
- [DEMO]()
- [Requisitos]()
- [Install]()
- [Componentes]()
- [Hardware Scheme]()
- [Arquitectura software]()
- [TO DO]()
- [Implementaciones adicionales]()
- [Licencia]()
- [Referencias]()

## Información del proyecto

Este proyecto busca crear un asistente robot completamente enfocado para la estimulación cognitiva con el usuario. Se realizará mediante un asistente de mesa con funcionalidades típicas ya existentes, pero gracias a la inteligencia artificial se podrá interactuar con él a través de voz.

Otro punto que queremos es que todo el software tenga que ser de código abierto, desde los modelos de aprendizaje profundo hasta las bibliotecas usadas. No necesita una conexión a Internet para utilizar la mayoría de sus funciones.

## Componentes

| [Pantalla](https://eu.robotshop.com/es/products/waveshare-7inch-qled-integrated-display-1024x600-w-dev-accessories?gad_source=1&gclid=CjwKCAjwkuqvBhAQEiwA65XxQPiNJrfmx6yoc__vxjiG-uWRSPLR4n9xQ5F9_rPI3Hyf-9Yth4KZohoC894QAvD_BwE) | [Alimentador 5V Raspberry](https://tienda.bricogeek.com/accesorios-raspberry-pi/813-alimentador-raspberry-pi-3-5v25a.html)     | [Cámara](https://tienda.bricogeek.com/accesorios-raspberry-pi/822-camara-raspberry-pi-v2-8-megapixels.html)                |
| :-------- | :------- | :------------------------- |
| ![pantalla](https://github.com/CarlosMelis/RLP-2324/assets/127751829/ae449b49-ea59-421d-aa6f-006a381ec182) | ![alimentador](https://github.com/CarlosMelis/RLP-2324/assets/127751829/17632609-ea4e-482d-9030-361675bf979f) | ![cámara](https://github.com/CarlosMelis/RLP-2324/assets/127751829/97d5126a-5617-47eb-a4c7-24c7c0dd4a8b)
| [Raspberry 3B+](https://tienda.bricogeek.com/placas-raspberry-pi/1089-raspberry-pi-3-b-plus.html) | [Pantalla ojos](https://www.amazon.es/AZDelivery-Pantalla-Display-pulgadas-Raspberry/dp/B01L9GC470/ref=sr_1_1?adgrpid=1306220248924282&dib=eyJ2IjoiMSJ9.v19U4AeB3MGCVIraHo-zd81DMAe-f4VgDWpHStVOH89BgQrDf4bhme6maPJvIGCNeCG1GaoJRbVYpyr5GfUfSvEJAf_WR2JKSemZ3i_LQRv3x_pJA4p7EH0kjK0-qPyaWn1fxuU7NJLpdnkicWjlXdU6E5xJAyfjzq5u4bpGPINAhWuAoIk13kKyKhZzJOCSlWas7FcO-nPqc3Yfy17P50oCyBC0CAouNGKvRFtMYN9dc_ekiMh-b-4QLwzoBLwQyNDfwQ-brxwQ1Ejm-kNgs3dICtYXZUUrRIv-40JDt-Q.Ahentau47hHdQZ_CYS5MuWGOoLolvxRVTBVbiLivxtk&dib_tag=se&hvadid=81638854262704&hvbmt=bp&hvdev=c&hvlocphy=3173&hvnetw=o&hvqmt=p&hvtargid=kwd-81639002330313%3Aloc-170&hydadcr=19344_1839968&keywords=pantalla+oled+raspberry&qid=1709760552&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1&smid=A1X7QLRQH87QA3)     | [Microfono](https://tienda.bricogeek.com/sensores-sonido/383-microfono-electret-preamplificado.html?search_query=microfono&results=20)                       |
| ![Raspberry](https://github.com/CarlosMelis/RLP-2324/assets/127751829/2c597496-b605-467a-9c1f-c71f5c0bff2e)| ![Pantalla_ojos](https://github.com/CarlosMelis/RLP-2324/assets/127751829/3d305659-71da-419a-b451-7ba04957436e)| ![Micro](https://github.com/CarlosMelis/RLP-2324/assets/127751829/dd1d7352-52bd-4b6f-b93e-00025f24b377)
| [Speaker](https://www.amazon.es/CQRobot-Speaker-Interface-Electronic-Projects/dp/B0822XCPT8/ref=sr_1_2?adgrpid=1297424156924450&dib=eyJ2IjoiMSJ9.H5SdoB4-Kfs01ojZN_EBc6_q5KgoCNZxDUmnvyWmz5WNqUFTan55N-u82dQoEIwZwePJHh0Op2y5WMayv3r6vcb7DcpbxvwslDQeJmt6lQbhpASBRq_aX-0atLmXwCZSLhBeRD_KLM7dHjJv5IqZvKOEef_6fe134uHwWg1tbx-nFeCrURGbtU3HIJfhIgyAYDPSf6R7AUM_4VQqSFo_sfo_ZaTDFRV7CWy6KiPpQ885fq5L9S8nowy_MvM3bKyi2zxmszNYxk5PH3GWfL4p-66dVq_x4hxmDM5ZtPZnp1c.Fea56L0PvfKRoTzEbHB9dzmD2dKF7J8yJBbZURD6I_k&dib_tag=se&hvadid=81089098768483&hvbmt=bp&hvdev=c&hvlocphy=3173&hvnetw=o&hvqmt=p&hvtargid=kwd-81089247644590%3Aloc-170&hydadcr=13813_1871987&keywords=speaker%2Braspberry%2Bpi&qid=1709759252&sr=8-2&th=1) | [Disipadores](https://tienda.bricogeek.com/accesorios-raspberry-pi/1087-pack-disipadores-para-raspberry-pi-3b.html) | [Servo](https://tienda.bricogeek.com/servomotores/1319-micro-servo-feetech-07kg-fs0403-fb-con-feedback.html)
| ![Speaker](https://github.com/CarlosMelis/RLP-2324/assets/127751829/ca82f3d9-319c-4d87-828c-559b8af7a980) | ![Disipadores](https://github.com/CarlosMelis/RLP-2324/assets/127751829/916dd0d5-8f6a-4553-b947-21cc34385ad7) | ![Servo](https://github.com/CarlosMelis/RLP-2324/assets/127751829/5d6f7b40-8681-4eea-a047-45419fd561d3)


## Hardware Scheme

![Hardware Scheme](https://github.com/CarlosMelis/RLP-2324/assets/127751829/b9f6236d-21c6-4dde-bfb3-96e3a156b473)

## Arquitectura software

![Arquitectura software](https://github.com/CarlosMelis/RLP-2324/assets/127751829/318bdf87-2a17-4267-99f4-93ab75b851d6)



## Support

- [Escola d'Enginyeria - UAB Barcelona](https://www.uab.cat/enginyeria/)
- [UAB Open Labs](https://www.uab.cat/open-labs/)

## Authors

- Javier Comes
- David Bonilla
- Carlos Alejandro Melis
- Adrián Gonzalez
