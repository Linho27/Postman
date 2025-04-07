#!/usr/bin/env python3  
# Sistema com múltiplos códigos e monitoramento contínuo de peças

from modules.fan import *
from modules.leds import *
from modules.switches import *
from modules.connection import *
import RPi.GPIO as GPIO                     # type: ignore
import multiprocessing
import time
import sys

# Subprocesso que monitora desconexões de peças
def monitorar_desconexoes(posicoes_monitoradas, flag_monitoramento):
    desconectadas = set()
    while flag_monitoramento.is_set():
        estados = getSwitches()
        for pos in posicoes_monitoradas:
            if estados[pos - 1] == 1:  # Switch solto
                if pos not in desconectadas:
                    print(f"⚠️ Peça removida da posição {pos}")
                    desconectadas.add(pos)
                # Pisca vermelho
                activate_segment(pos, RED)
            else:
                if pos in desconectadas:
                    print(f"✅ Peça recolocada na posição {pos}")
                    desconectadas.remove(pos)
                rightPos(pos)
        time.sleep(0.3)

def main():
    try:
        print("Sistema de gerenciamento de placas iniciando...")
        tempChecking = multiprocessing.Process(target=check_temp, daemon=True)
        tempChecking.start()
        startUp()

        scanned_codes = {}

        while True:
            print("\nModo de escaneamento - escaneie os códigos de uma vez")
            print("Para iniciar a verificação, pressione o primeiro switch desejado")

            current_states = getSwitches()
            initial_pressed = [i+1 for i, state in enumerate(current_states) if state == 0]

            if initial_pressed:
                print("Pressionamento detectado. Iniciando verificação.")
                break

            code = input("Escanear código QR/Barra: ").strip()

            if code in scanned_codes:
                print(f"Código {code} já escaneado!")
                continue

            platePosition = getPos(code)

            if not platePosition.isdigit() or int(platePosition) < 1 or int(platePosition) > 12:
                print(f"Código inválido: {platePosition}")
                continue

            platePosition = int(platePosition)

            if isOccupied(platePosition):
                print(f"Posição {platePosition} ocupada!")
                continue

            scanned_codes[code] = platePosition
            print(f"PS-{platePosition:03d}")
            indicateRightPos(platePosition)

        print("\nIniciando verificação por etapas...")
        remaining_positions = list(scanned_codes.values())

        while remaining_positions:
            current_pos = remaining_positions[0]
            print(f"\nVerificando posição {current_pos}...")
            indicateRightPos(current_pos)

            pressed = False
            while not pressed:
                current_states = getSwitches()
                pressed_switches = [i+1 for i, state in enumerate(current_states) if state == 0]

                if current_pos in pressed_switches:
                    pressed = True
                    rightPos(current_pos)
                    togglePos(current_pos)
                    print("Posição confirmada! (Verde)")

                    released = False
                    while True:
                        current_states = getSwitches()
                        if current_pos not in [i+1 for i, state in enumerate(current_states) if state == 0]:
                            released = True
                            warnOccupiedPos(current_pos)
                            print("ERRO: Switch solto! (Vermelho)")

                            while current_pos not in [i+1 for i, state in enumerate(getSwitches()) if state == 0]:
                                time.sleep(0.1)

                            rightPos(current_pos)
                            print("Switch pressionado novamente! (Verde)")
                        elif released:
                            break
                        time.sleep(0.1)

                    remaining_positions.pop(0)
                    break

                wrong_positions = [pos for pos in pressed_switches if pos in remaining_positions and pos != current_pos]
                if wrong_positions:
                    warnWrongPos(current_pos, wrong_positions)
                    print(f"ERRO: Posição errada pressionada: {wrong_positions}")
                    time.sleep(2)
                    indicateRightPos(current_pos)

                time.sleep(0.1)

        print("\nTodas as posições verificadas com sucesso!")

        # Iniciar subprocesso de monitoramento contínuo
        flag_monitoramento = multiprocessing.Event()
        flag_monitoramento.set()
        monitor_proc = multiprocessing.Process(
            target=monitorar_desconexoes,
            args=(list(scanned_codes.values()), flag_monitoramento),
            daemon=True
        )
        monitor_proc.start()

        print("⚙️ Monitoramento contínuo de peças iniciado.")
        print("Pressione Ctrl+C para encerrar o sistema.")

        while True:
            time.sleep(1)

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
