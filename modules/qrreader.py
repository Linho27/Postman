#Switches controll module

# Libraries import
import cv2
import numpy as np
from pyzbar.pyzbar import decode            #type: ignore
from picamera2 import Picamera2             #type: ignore

# Function to read QR code and return its value
def ler_qr():
    # Start camera with lower resolution to not stress the Raspberry Pi
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (320, 240)})
    picam2.configure(config)
    picam2.start()

    while True:
        frame = picam2.capture_array()                  # Capture camera image
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert to BGR color scheme

        # Detect and decode QR code
        qrCodes = decode(frame)
        for qr in qrCodes:
            data = qr.data.decode('utf-8')
            picam2.stop()
            return data  # Return read QR code
        
codigo_qr = ler_qr()
print(f"Código QR Detetado: {codigo_qr}")
