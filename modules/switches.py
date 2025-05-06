# ================================
# 🔗 Switches control module
# ================================

# ================================
# 📦 Imports
# ================================
import os
import time
import RPi.GPIO as GPIO  # type: ignore
from dotenv import load_dotenv
from typing import List, Dict
from modules.connection import *

# ================================
# 🔐 Environment Variables
# ================================
load_dotenv()
SWITCHES_PINS = os.getenv("SWITCHES_PINS")

if SWITCHES_PINS is None:
    raise ValueError("Variável de ambiente 'SWITCHES_PINS' não definida.")
# Espera-se uma string como "4,17,27,22,..."
SWITCHES_PINS = [int(pin.strip()) for pin in SWITCHES_PINS.split(",")]

# ================================
# ⚙️ GPIO Initialization
# ================================
_initialized = False

def _init_gpio():
    global _initialized
    if not _initialized:
        GPIO.setmode(GPIO.BCM)
        for pin in SWITCHES_PINS:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        _initialized = True

# ================================
# ▶️ Functions
# ================================

def getSwitches() -> List[int]:
    """Retorna os estados brutos de todos os switches (1=solto, 0=pressionado)."""
    _init_gpio()
    return [GPIO.input(pin) for pin in SWITCHES_PINS]

def compareSwitches(oldStates: List[int]) -> List[int]:
    """Compara estados atuais com anteriores. Retorna índices das mudanças."""
    current = getSwitches()
    return [i for i in range(len(SWITCHES_PINS)) if current[i] != oldStates[i]]

def didntChange(states: List[int]) -> bool:
    """Verifica se não houve mudanças nos estados."""
    return len(states) == 0

def update_positions() -> Dict[int, bool]:
    """
    Retorna um dicionário {posição: ocupada}
    ocupada=True se pressionado (GPIO=0)
    """
    states = getSwitches()
    return {pos+1: (state == 0) for pos, state in enumerate(states)}

def syncSwitchesWithAPI() -> Dict[int, bool]:
    """
    Sincroniza todos os switches físicos com o estado da API.
    Se houver diferença, faz o toggle na API.
    Retorna dicionário {posição: resultado_toggle}
    """
    _init_gpio()
    results = {}
    current_states = getSwitches()
    for position in range(1, len(SWITCHES_PINS)+1):
        pin = SWITCHES_PINS[position-1]
        physical_state = current_states[position-1] == 0  # 0 = pressionado
        api_state = isOccupied(position)
        if physical_state != api_state:
            result = togglePos(position)
            results[position] = result
    return results

def cleanup():
    """Limpa recursos do GPIO."""
    global _initialized
    if _initialized:
        GPIO.cleanup()
        _initialized = False