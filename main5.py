# ================================
# 🔐 Variáveis de ambiente
# ================================
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("BASE_API")

# ================================
# 📦 Imports
# ================================

from modules.leds import *
from modules.fan import *
from modules.switches import *
from modules.connection import *
import RPi.GPIO as GPIO                 # type: ignore
import multiprocessing
import time
import sys
import requests

# ================================
# ⚙️ Funções Background
# ================================













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
