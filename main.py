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
from time import sleep
import sys

# ================================
# ⚙️ Background Functions
# ================================
def monitorSwitches():
    print("[Monitor] Processo de verificação de mudanças iniciado.")
    previous_states = getSwitches()

    while True:
        try:
            changed = compareSwitches(previous_states)
            if didntChange(changed):
                sleep(0.1)
                continue

            for idx in changed:
                pos = idx + 1
                current = getSwitches()[idx]

                if current == 0:
                    # Switch pressionado (ocupado)
                    print(f"[Monitor] Detetado NOVO ocupado na posição {pos}")
                    indicateRightPos(pos)
                else:
                    # Switch libertado (desocupado)
                    print(f"[Monitor] Posição {pos} agora está LIVRE")
                    deactivate_segment(pos)

            previous_states = getSwitches()
            sleep(0.1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[Erro no monitor] {e}")
            sleep(1)

# ================================
# ⭐ Main code
# ================================
if __name__ == "__main__":
    try:
        print("[Sistema] Início do programa")
        ledsOff()

        print("[Sistema] Sincronização inicial com a API...")
        resultado_sync = syncSwitchesWithAPI()
        print(f"[Sync Resultado] {resultado_sync}")

        print("[Sistema] Teste de arranque dos LEDs")
        startUpLEDS()

        # Iniciar processo para vigiar mudanças locais
        monitorProcess = multiprocessing.Process(target=monitorSwitches, daemon=True)
        monitorProcess.start()

        while True:
            print("\n[Main] Aguardando leitura de código de barras...")
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

            print("[Main] À espera de mudança de switch...")
            oldStates = getSwitches()
            while True:
                changed = compareSwitches(oldStates)
                if not didntChange(changed):
                    if (pos - 1) in changed:
                        current = getSwitches()[pos - 1]
                        if current == 0:
                            print("[Main] Colocada na posição CORRETA!")
                            rightPos(pos)
                            break
                        else:
                            print("[Main] Retirada da posição correta.")
                            deactivate_segment(pos)
                            break
                    else:
                        wrong_pos = changed[0] + 1
                        print(f"[Main] Colocada na posição ERRADA: {wrong_pos}")
                        warnWrongPos(pos, wrong_pos)
                        print("[Main] À espera que a errada seja removida...")
                        while getSwitches()[wrong_pos - 1] == 0:
                            sleep(0.1)
                        print("[Main] Errada removida.")
                        indicateRightPos(pos)
                        oldStates = getSwitches()
                sleep(0.1)

    except KeyboardInterrupt:
        print("\n[Sistema] Interrompido pelo utilizador.")
    finally:
        ledsOff()
        cleanup()
        sys.exit(0)
