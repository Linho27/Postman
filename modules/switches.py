# ================================
# 🔗 Switches control module
# ================================

# ================================
# 📦 Imports
# ================================
import os
import time
import ast
import RPi.GPIO as GPIO  # type: ignore
from dotenv import load_dotenv
from typing import List, Dict
from modules.connection import *

# ================================
# 🔐 Environment Variables
# ================================
load_dotenv()
SWITCHES_PINS_RAW = os.getenv("SWITCHES_PINS")

if SWITCHES_PINS_RAW is None:
    raise ValueError("Variável de ambiente 'SWITCHES_PINS' não definida.")

# DEBUG: Mostra o valor lido da variável de ambiente
print("DEBUG SWITCHES_PINS_RAW:", repr(SWITCHES_PINS_RAW))

try:
    parsed_list = ast.literal_eval(SWITCHES_PINS_RAW)
    if not isinstance(parsed_list, list):
        raise ValueError
    SWITCHES_PINS = [int(pin) for pin in parsed_list]
except (ValueError, SyntaxError):
    raise ValueError(f"Formato inválido para SWITCHES_PINS: {SWITCHES_PINS_RAW}")

if not SWITCHES_PINS:
    raise ValueError("Nenhum pino válido foi encontrado em 'SWITCHES_PINS'.")

print("DEBUG SWITCHES_PINS (lista final):", SWITCHES_PINS)

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
    _init_gpio()
    return [GPIO.input(pin) for pin in SWITCHES_PINS]

def compareSwitches(oldStates: List[int]) -> List[int]:
    current = getSwitches()
    return [i for i in range(len(SWITCHES_PINS)) if current[i] != oldStates[i]]

def didntChange(states: List[int]) -> bool:
    return len(states) == 0

def update_positions() -> Dict[int, bool]:
    states = getSwitches()
    return {pos+1: (state == 0) for pos, state in enumerate(states)}

def syncSwitchesWithAPI() -> Dict[int, bool]:
    _init_gpio()
    results = {}
    current_states = getSwitches()
    for position in range(1, len(SWITCHES_PINS)+1):
        pin = SWITCHES_PINS[position-1]
        physical_state = current_states[position-1] == 0
        api_state = isOccupied(position)
        if physical_state != api_state:
            result = togglePos(position)
            results[position] = result
    return results

def cleanup():
    global _initialized
    if _initialized:
        GPIO.cleanup()
        _initialized = False
