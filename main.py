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
import RPi.GPIO as GPIO
import multiprocessing
from multiprocessing import Value
from time import sleep
import sys

# ================================
# ⚙️ Background function
# ================================
def monitorOutOfSyncSwitches(waiting):
    print("[Monitor] Início da verificação contínua com a API.")
    try:
        while True:
            if waiting.value:
                # Pausa o monitor enquanto o main está à espera de colocação
                sleep(0.5)
                continue

            sleep(1)
            states_local = getSwitches()
            for idx, gpio_state in enumerate(states_local):
                pos = idx + 1
                physical_occupied = (gpio_state == 0)
                api_occupied = isOccupied(pos)

                if physical_occupied != api_occupied:
                    print(f"[Monitor] Desincronizado na posição {pos}")
                    warnOccupiedPos(pos)
                else:
                    deactivate_segment(pos)
    except KeyboardInterrupt:
        print("[Monitor] Terminado.")
    except Exception as e:
        print(f"[Monitor] Erro: {e}")

# ================================
# ⭐ Main code
# ================================
if __name__ == "__main__":
    try:
        print("[Sistema] Início do programa.")
        ledsOff()

        print("[Sistema] Sincronização inicial com a API...")
        resultado_sync = syncSwitchesWithAPI()
        print(f"[Sync Resultado] {resultado_sync}")

        print("[Sistema] Teste de arranque dos LEDs")
        startUpLEDS()

        # Cria variável partilhada
        waiting = Value('b', False)

        # Inicia processo de monitorização contínua com comparação à API
        monitorProcess = multiprocessing.Process(target=monitorOutOfSyncSwitches, args=(waiting,), daemon=True)
        monitorProcess.start()

        while True:
            print("\n[Main] À espera da leitura do código de barras...")
            id_input = input("Introduz o código de barras: ").strip()
            if id_input.lower() in ("exit", "quit"):
                print("[Sistema] A sair.")
                break

            pos = getPos(id_input)
            if isinstance(pos, str):
                print(f"[Erro] {pos}")
                continue

            if not (1 <= pos <= 12):
                print(f"[Erro] Posição inválida devolvida pela API: {pos}")
                continue

            print(f"[Main] Código {id_input} corresponde à posição {pos}.")
            indicateRightPos(pos)

            print("[Main] À espera da colocação na posição correta...")
            oldStates = getSwitches()

            waiting.value = True  # Sinaliza ao monitor para parar notificações

            while True:
                sleep(0.1)
                changed = compareSwitches(oldStates)
                if didntChange(changed):
                    continue

                if (pos - 1) in changed:
                    current = getSwitches()[pos - 1]
                    if current == 0:
                        print("[Main] Colocada na posição correta!")
                        rightPos(pos)
                        togglePos(pos)
                        waiting.value = False
                        break
                    else:
                        print("[Main] Retirada da posição correta.")
                        rightPos(pos)
                        togglePos(pos)
                        waiting.value = False
                        break
                else:
                    wrong_pos = changed[0] + 1
                    print(f"[Main] Colocada na posição errada: {wrong_pos}")
                    warnWrongPos(pos, wrong_pos)
                    print("[Main] À espera que a errada seja removida...")
                    while getSwitches()[wrong_pos - 1] == 0:
                        sleep(0.1)
                    print("[Main] Errada removida.")
                    indicateRightPos(pos)
                    oldStates = getSwitches()

    except KeyboardInterrupt:
        print("\n[Sistema] Interrompido pelo utilizador.")
    finally:
        ledsOff()
        cleanup()
        sys.exit(0)
