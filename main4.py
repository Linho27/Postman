#!/usr/bin/env python3  
# Sistema com múltiplos códigos, monitoramento contínuo de peças e verificação com API

from modules.fan import *
from modules.leds import *
from modules.switches import *
from modules.connection import *
import RPi.GPIO as GPIO                     # type: ignore
import multiprocessing
import time
import sys
import requests  # Para chamadas à API

API_BASE = 'http://192.168.30.207'

# ====== Funções auxiliares para integração com API ======

def get_expected_switch_states():
    """Consulta o estado esperado de cada posição na API."""
    try:
        response = requests.get(f'{API_BASE}/everyPlate')
        if response.status_code == 200:
            return response.json()  # Exemplo: [1, 1, 0, 1, ...]
        else:
            print("Erro ao consultar estados dos switches na API.")
            return None
    except Exception as e:
        print(f"Erro ao consultar API: {e}")
        return None

def get_pos_from_api(code):
    """
    Consulta a posição correta do código na API.
    Assumindo que o código de barras é o número da posição.
    Se não for, substitua esta função conforme a lógica da sua API.
    """
    try:
        # Se o código de barras é o número da posição:
        pos = int(code)
        # Verifica se a posição existe na API
        response = requests.get(f'{API_BASE}/status/{pos}')
        if response.status_code == 200:
            return pos
        else:
            print("Posição não encontrada na API.")
            return None
    except Exception as e:
        print(f"Erro ao consultar API: {e}")
        return None

def toggle_position(pos):
    """Envia comando para alternar o estado da posição na API."""
    try:
        response = requests.post(f'{API_BASE}/toggle/{pos}')
        if response.status_code == 200:
            print(f"Toggle enviado para posição {pos}.")
        else:
            print(f"Falha ao alternar posição {pos}.")
    except Exception as e:
        print(f"Erro ao alternar posição {pos}: {e}")

# ====== Subprocesso para verificação contínua de sincronização switch-API ======

def check_switch_api_sync(flag_monitoramento):
    """Verifica continuamente se o estado físico dos switches corresponde ao estado da API."""
    while flag_monitoramento.is_set():
        expected_states = get_expected_switch_states()
        if expected_states is None:
            time.sleep(1)
            continue
        current_states = getSwitches()
        for i, (expected, current) in enumerate(zip(expected_states, current_states)):
            pos = i + 1
            if expected != current:
                # Acionar LED intermitente na posição em não conformidade
                blink_led(pos, color=YELLOW)
            else:
                # Apagar LED de erro se estiver aceso
                rightPos(pos)
        time.sleep(1)

# ====== Função principal ======

def main():
    try:
        print("Sistema de gerenciamento de placas iniciando...")
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
                        rightPos(platePosition)
                        print("Posição correta verificada! (Verde)")
                        toggle_position(platePosition)  # Alterna na API
                        break  # Avança para o próximo código
                    else:
                        # Posição errada pressionada
                        for pos in pressed_switches:
                            blink_led(pos, color=RED)
                        blink_led(platePosition, color=YELLOW)
                        print(f"ERRO: Switch errado pressionado: {pressed_switches}. Remova a placa errada.")

                        # Aguarda a remoção do switch errado
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
