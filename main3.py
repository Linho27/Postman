#!/usr/bin/env python3 
# Sistema completo de gerenciamento de placas com integração de todos os módulos

from modules.fan import *
from modules.leds import *
from modules.switches import *
from modules.connection import *
import RPi.GPIO as GPIO                     # type: ignore
import multiprocessing
import time
import sys

def monitor_switches(shared_pressed):
    """Monitorar switches pressionados em tempo real"""
    print("Monitoramento de switches iniciado...")
    while True:
        current_states = getSwitches()
        for pos in range(12):
            if current_states[pos] == 0:  # Pressionado
                shared_pressed[pos] = True
            else:
                if shared_pressed.get(pos):
                    print(f"Switch da posição {pos+1} foi solto!")

                    # Iniciar LED de erro em processo paralelo
                    p = multiprocessing.Process(target=warnOccupiedPos, args=(pos+1,), daemon=True)
                    p.start()

                    shared_pressed[pos] = False
        time.sleep(0.2)

def main():
    try:
        print("Sistema de gerenciamento de placas iniciando...")

        # Gerenciador para memória compartilhada entre processos
        manager = multiprocessing.Manager()
        pressed_positions = manager.dict()

        # Processo 1: Verificação da temperatura
        tempChecking = multiprocessing.Process(target=check_temp, daemon=True)
        tempChecking.start()

        # Processo 2: Monitoramento contínuo dos switches
        switch_monitor = multiprocessing.Process(target=monitor_switches, args=(pressed_positions,), daemon=True)
        switch_monitor.start()

        # Teste inicial dos LEDs
        startUp()

        while True:
            code = input("Aguardando leitura de código QR/Barra (ou digite 404 para sair): ").strip()
            if code == '404':
                break

            syncSwitchesWithAPI()

            # Obter posição correta da placa via API
            platePosition = getPos(code)
            if not str(platePosition).isdigit() or int(platePosition) < 1 or int(platePosition) > 12:
                print(f"Código inválido ou placa não encontrada: {platePosition}")
                warnOccupiedPos(1)
                continue

            platePosition = int(platePosition)

            if isOccupied(platePosition):
                print(f"Posição {platePosition} está ocupada!")
                warnOccupiedPos(platePosition)
                continue

            indicateRightPos(platePosition)

            print(f"Aguardando colocação da placa na posição {platePosition}...")

            # Espera até o switch da posição correta ser pressionado
            while True:
                switches = getSwitches()
                if switches[platePosition - 1] == 0:
                    print("Placa colocada corretamente!")
                    rightPos(platePosition)
                    togglePos(platePosition)
                    pressed_positions[platePosition - 1] = True
                    break
                time.sleep(0.2)

    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
    finally:
        GPIO.cleanup()
        ledsOff()
        print("Sistema encerrado corretamente.")
        sys.exit(0)

if __name__ == "__main__":
    main()