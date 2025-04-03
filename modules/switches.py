# switches.py - Versão compatível com o main existente
import RPi.GPIO as GPIO
import time
from typing import List, Dict
from modules.connection import togglePos, isOccupied

# Configuração dos pinos (BCM numbering)
switches_pins = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13]  # Pinos 1-12

# Variável global para controle de inicialização
_initialized = False

def _init_gpio():
    global _initialized
    if not _initialized:
        GPIO.setmode(GPIO.BCM)
        for pin in switches_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        _initialized = True

def syncSwitchesWithAPI():
    """Sincroniza todos os switches com a API"""
    _init_gpio()
    results = {}
    current_states = getSwitches()
    
    for position in range(1, 13):
        pin = switches_pins[position-1]
        physical_state = current_states[position-1] == 0  # 0 = pressionado
        api_state = isOccupied(position)
        
        if physical_state != api_state:
            result = togglePos(position)
            results[position] = result
    
    return results

# Funções originais mantidas para compatibilidade
def getSwitches():
    """Retorna estados brutos de todos os switches"""
    _init_gpio()
    return [GPIO.input(pin) for pin in switches_pins]

def compareSwitches(oldStates):
    """Compara com estados anteriores"""
    current = getSwitches()
    return [i for i in range(12) if current[i] != oldStates[i]]

def didntChange(states):
    """Verifica se não houve mudanças"""
    return len(states) == 0

def update_positions():
    """Atualiza e retorna estados de todas as posições"""
    states = getSwitches()
    return {pos+1: (state == 0) for pos, state in enumerate(states)}

def cleanup():
    """Limpeza dos recursos GPIO"""
    if _initialized:
        GPIO.cleanup()