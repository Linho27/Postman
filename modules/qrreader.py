#Switches controll module

# Libraries import
import cv2
import numpy as np
from pyzbar.pyzbar import decode            #type: ignore
from picamera2 import Picamera2             #type: ignore

# Function to read QR code and return its value
def readQr():
    # Iniciar a câmara com resolução mais baixa para não sobrecarregar o Raspberry Pi
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (320, 240)})
    picam2.configure(config)
    picam2.start()
    
    data = None
    
    while data is None:
        frame = picam2.capture_array()                  # Capturar imagem da câmara
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Converter para esquema de cores BGR

        # Detetar e descodificar código QR
        qrCodes = decode(frame)
        for qr in qrCodes:
            data = qr.data.decode('utf-8')
            break  # Sair do loop assim que encontrar um código QR
    
    picam2.stop()
    return data  # Retornar o código QR lido