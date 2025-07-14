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

# ================================
# ⚙️ Background Function
# ================================
def outOfSyncSwitches():
    """
    Verifica continuamente se os switches físicos estão em sincronia com a API.
    Se não estiverem, activa LED intermitente na posição desincronizada.
    """
    while True:
        sleep(2)
        try:
            diffs = syncSwitchesWithAPI()
            for pos, result in diffs.items():
                if result:  # Houve toggle → estava fora de sincronia
                    warnOccupiedPos(pos)
        except Exception as e:
            print(f"[Erro no processo de fundo] {e}")

# ================================
# ⭐ Main code
# ================================
if __name__ == "__main__":
    try:
        startUpLEDS()
        print("[Sistema iniciado]")

        # Processo de verificação de sincronização
        outOfSyncProcess = multiprocessing.Process(target=outOfSyncSwitches, daemon=True)
        outOfSyncProcess.start()

        while True:
            # 1️⃣ Ler código de barras
            id_input = input("\n[Leitura] Introduz o código de barras da peça (ou 'sair'): ").strip()
            if id_input.lower() == "sair":
                break

            # 2️⃣ Obter posição correcta via API
            pos = getPos(id_input)
            if isinstance(pos, str):
                print(f"[Erro] {pos}")
                continue
            try:
                pos = int(pos)
            except ValueError:
                print("[Erro] Resposta inválida da API.")
                continue

            if not (1 <= pos <= 12):
                print(f"[Erro] Posição inválida devolvida pela API: {pos}")
                continue

            print(f"[Info] Coloca a peça na posição {pos}.")
            indicateRightPos(pos)

            # 3️⃣ Esperar mudança de estado nos switches
            prev_states = getSwitches()
            while True:
                sleep(0.2)
                changed = compareSwitches(prev_states)
                if not didntChange(changed):
                    break
            current_states = getSwitches()

            # 4️⃣ Verificar se o switch certo foi activado
            occupied_map = update_positions()
            if occupied_map.get(pos):
                # ✅ Colocado na posição certa
                print("[Sucesso] Peça colocada no local correcto!")
                rightPos(pos)
                continue

            # ❌ Colocada na posição errada
            wrong_pos = None
            for p, occupied in occupied_map.items():
                if occupied:
                    wrong_pos = p
                    break

            if wrong_pos is not None:
                print(f"[Aviso] Peça colocada no local errado: {wrong_pos}")
                warnWrongPos(pos, wrong_pos)

                # 5️⃣ Esperar que a peça errada seja retirada
                while True:
                    sleep(0.5)
                    occupied_map = update_positions()
                    if not occupied_map.get(wrong_pos):
                        print("[Info] Peça removida da posição errada. Retoma o processo.")
                        break

            # Volta ao início do loop principal

    except KeyboardInterrupt:
        print("\n[Encerramento manual]")
    finally:
        ledsOff()
        cleanup()
        print("[Sistema desligado com segurança]")
