# ================================
# 🔐 Environment Variables
# ================================
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("BASE_API")

# ================================
# 📦 Imports
# ================================

from modules.leds import *
from modules.switches import *
from modules.connection import *
import RPi.GPIO as GPIO                 # type: ignore
import multiprocessing
from time import sleep
import sys
import requests

# ================================
# ⚙️ Background Functions
# ================================

def outOfSyncSwitches():
    while True:
        print("Debug#2")
        sleep(1)


# ================================
# ⭐ Main code
# ================================

if __name__ == "__main__":
    outOfSyncChecking = multiprocessing.Process(target=outOfSyncSwitches, daemon=True)
    outOfSyncChecking.start()
    while True:
        print("Debug#1")
        sleep(1)





        """
        --Sempre a correr de fundo

            Verificação se estado do switch está igual à api
            Caso não seja
                Ligar led intermitente em não correspondencia

        --Main

            Ler código de barras
            Contactar com a api para receber a posição do código
            Ligar leds na posição correta
            Aguardar mudança de estado de algum switch
            Caso switch seja o correto
                Ligar luz de verificação de posição correta
            Caso switch seja o errado
                Ligar luz intermitente na posição correta e errada
                Aguardar a placa da posição errada ser removida
                Voltar para o passo anterior
        """
