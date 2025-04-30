#!/usr/bin/env python3

from modules.leds import *
from modules.fan import *
from modules.switches import *
from modules.connection import *
import RPi.GPIO as GPIO
import multiprocessing
import time
import sys
import requests

API_BASE = 'http://192.168.30.207:5000'

def get_expected_switch_states():
    try:
        response = requests.get(f'{API_BASE}/everyPlate', timeout=2)
        if response.status_code == 200:
            return response.json()
        else:
            print("Erro ao consultar estados dos switches na API.")
            return None
    except Exception as e:
        print(f"Erro ao consultar API: {e}")
        return None

def get_pos_from_api(code):
    try:
        response = requests.get(f'{API_BASE}/everyPlate', timeout=2)
        if response.status_code == 200:
            placas = response.json()
            print("DEBUG placas:", placas, type(placas))
            if isinstance(placas, dict):
                for pos_str, info in placas.items():
                    # info deve ser um dicionário com o campo 'id'
                    if isinstance(info, dict) and info.get('id') == code:
                        # pos_str é a posição como string, converte para inteiro
                        return int(pos_str)
            print("Código não encontrado na API.")
            return None
        else:
            print("Erro ao consultar todas as placas na API.")
            return None
    except Exception as e:
        print(f"Erro ao consultar API: {e}")
        return None

def toggle_position(pos):
    try:
        response = requests.post(f'{API_BASE}/toggle/{pos}', timeout=2)
        if response.status_code == 200:
            print(f"Toggle enviado para posição {pos}.")
        else:
            print(f"Falha ao alternar posição {pos}.")
    except Exception as e:
        print(f"Erro ao alternar posição {pos}: {e}")

def check_switch_api_sync(flag_monitoramento):
    expected_states = get_expected_switch_states()
    current_states = getSwitches()
    if expected_states is None or current_states is None:
        last_discrepancy = set()
    else:
        last_discrepancy = set(
            i + 1 for i, (expected, current) in enumerate(zip(expected_states, current_states)) if expected != current
        )
    time.sleep(1)

    while flag_monitoramento.is_set():
        expected_states = get_expected_switch_states()
        if expected_states is None:
            time.sleep(1)
            continue
        current_states = getSwitches()
        if current_states is None:
            time.sleep(1)
            continue
        current_discrepancy = set(
            i + 1 for i, (expected, current) in enumerate(zip(expected_states, current_states)) if expected != current
        )
        new_discrepancy = current_discrepancy - last_discrepancy
        for pos in new_discrepancy:
            blink_led(pos, color=YELLOW)
        last_discrepancy = current_discrepancy
        time.sleep(1)

def main():
    try:
        print("Sistema de gerenciamento de placas iniciando...")
        ledsOff()
        tempChecking = multiprocessing.Process(target=check_temp, daemon=True)
        tempChecking.start()
        startUp()

        # Iniciar subprocesso de verificação contínua switch-API
        flag_sync = multiprocessing.Event()
        flag_sync.set()
        sync_proc = multiprocessing.Process(
            target=check_switch_api_sync,
            args=(flag_sync,),
            daemon=True
        )
        sync_proc.start()

        print("\nModo de operação: Escaneie o código de barras da placa.")

        while True:
            code = input("Escanear código de barras: ").strip()
            if not code:
                continue

            platePosition = get_pos_from_api(code)
            if platePosition is None or platePosition < 1 or platePosition > 12:
                print("Posição inválida ou não encontrada na API.")
                continue

            indicateRightPos(platePosition)
            print(f"Coloque a placa na posição {platePosition} e pressione o switch correspondente.")

            while True:
                current_states = getSwitches()
                pressed_switches = [i+1 for i, state in enumerate(current_states) if state == 0]
                if pressed_switches:
                    if platePosition in pressed_switches:
                        deactivate_segment(platePosition)  # Apaga o azul antes de acender o verde
                        rightPos(platePosition)
                        print("Posição correta verificada! (Verde)")
                        toggle_position(platePosition)
                        ledsOff()  # Garante tudo apagado antes de avançar
                        break
                    else:
                        for pos in pressed_switches:
                            blink_led(pos, color=RED)
                        blink_led(platePosition, color=YELLOW)
                        print(f"ERRO: Switch errado pressionado: {pressed_switches}. Remova a placa errada.")
                        # Espera até todos os switches errados serem liberados
                        while True:
                            current_states = getSwitches()
                            still_wrong = [pos for pos in pressed_switches if current_states[pos-1] == 0]
                            if not still_wrong:
                                break
                            time.sleep(0.1)
                        indicateRightPos(platePosition)
                time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
    finally:
        GPIO.cleanup()
        ledsOff()
        for p in multiprocessing.active_children():
            p.terminate()
        print("Sistema encerrado corretamente.")
        sys.exit(0)

if __name__ == "__main__":
    main()
