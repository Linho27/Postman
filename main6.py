import os
import sys
import time
import signal
import logging
import requests
import multiprocessing
import RPi.GPIO as GPIO

from dotenv import load_dotenv
from typing import List, Dict, Optional
from modules.leds import *
from modules.switches import *
from modules.connection import *

# ================================
# 🌐 Configuração Geral
# ================================
API_BASE = 'http://192.168.30.207:5000'

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# ================================
# ⚖️ Funções auxiliares
# ================================
def get_expected_switch_states() -> Optional[Dict[int, bool]]:
    try:
        response = requests.get(f'{API_BASE}/everyPlate', timeout=2)
        if response.status_code == 200:
            data = response.json()
            return {int(pos): info.get('estado', False) for pos, info in data.items() if isinstance(info, dict)}
        logging.error("Erro ao consultar estados dos switches na API.")
    except Exception as e:
        logging.error(f"Erro ao consultar API: {e}")
    return None

def get_pos_from_api(code: str) -> Optional[int]:
    try:
        response = requests.get(f'{API_BASE}/everyPlate', timeout=2)
        if response.status_code == 200:
            placas = response.json()
            for pos_str, info in placas.items():
                if isinstance(info, dict) and info.get('id') == code:
                    return int(pos_str)
        logging.warning("Código não encontrado na API.")
    except Exception as e:
        logging.error(f"Erro ao consultar API: {e}")
    return None

def toggle_position(pos: int) -> None:
    try:
        response = requests.post(f'{API_BASE}/toggle/{pos}', timeout=2)
        if response.status_code == 200:
            logging.info(f"Toggle enviado para posição {pos}.")
        else:
            logging.warning(f"Falha ao alternar posição {pos}.")
    except Exception as e:
        logging.error(f"Erro ao alternar posição {pos}: {e}")

def check_switch_api_sync(flag_monitoramento: multiprocessing.Event):
    last_discrepancy = set()
    while flag_monitoramento.is_set():
        expected_states = get_expected_switch_states()
        current_states_raw = getSwitches()

        if expected_states is None or current_states_raw is None:
            time.sleep(1)
            continue

        current_states = {i + 1: (state == 0) for i, state in enumerate(current_states_raw)}

        current_discrepancy = {pos for pos, expected in expected_states.items() if current_states.get(pos) != expected}
        new_discrepancy = current_discrepancy - last_discrepancy

        for pos in new_discrepancy:
            blink_segment(pos, color=YELLOW)

        last_discrepancy = current_discrepancy
        time.sleep(1)

# ================================
# 🚀 Função principal
# ================================
def main():
    def handle_exit(*_):
        logging.info("Encerrando sistema...")
        GPIO.cleanup()
        ledsOff()
        for p in multiprocessing.active_children():
            p.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    logging.info("Sistema de gerenciamento de placas iniciando...")
    ledsOff()
    startUpLEDS()

    flag_sync = multiprocessing.Event()
    flag_sync.set()
    sync_proc = multiprocessing.Process(
        target=check_switch_api_sync,
        args=(flag_sync,),
        daemon=True
    )
    sync_proc.start()

    logging.info("Modo de operação: Escaneie o código de barras da placa.")

    while True:
        code = input("Escanear código de barras: ").strip()
        if not code:
            continue

        plate_position = get_pos_from_api(code)
        if plate_position is None or plate_position not in range(1, 13):
            logging.warning("Posição inválida ou não encontrada na API.")
            continue

        indicateRightPos(plate_position)
        logging.info(f"Coloque a placa na posição {plate_position} e pressione o switch correspondente.")

        while True:
            current_states = getSwitches()
            pressed = [i + 1 for i, state in enumerate(current_states) if state == 0]

            if pressed:
                if plate_position in pressed:
                    deactivate_segment(plate_position)
                    rightPos(plate_position)
                    logging.info("Posição correta verificada! (Verde)")
                    toggle_position(plate_position)
                    ledsOff()
                    break
                else:
                    for pos in pressed:
                        blink_segment(pos, RED)
                    blink_segment(plate_position, YELLOW)
                    logging.warning(f"ERRO: Switch errado pressionado: {pressed}. Remova a placa errada.")

                    while True:
                        current_states = getSwitches()
                        still_wrong = [pos for pos in pressed if current_states[pos - 1] == 0]
                        if not still_wrong:
                            break
                        time.sleep(0.1)

                    indicateRightPos(plate_position)
            time.sleep(0.1)

if __name__ == "__main__":
    main()
