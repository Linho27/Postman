#!/usr/bin/env python3 
# Sistema de gerenciamento com feedback visual em 3 etapas

from modules.fan import *
from modules.leds import *
from modules.switches import *
from modules.connection import *
import RPi.GPIO as GPIO                     # type: ignore
import multiprocessing
import time
import sys

def main():
    try:
        # Inicialização do sistema
        print("Sistema de gerenciamento de placas iniciando...")
        
        # Controle de temperatura
        tempChecking = multiprocessing.Process(target=check_temp, daemon=True)
        tempChecking.start()
        
        # Teste inicial dos LEDs
        startUp()
        
        while True:
            # ETAPA 1: Leitura do código e indicação da posição
            previous_states = getSwitches()
            code = input("Aguardando leitura de código (ou digite 404 para sair): ").strip()
            
            syncSwitchesWithAPI()

            if code == '404':
                break
                
            platePosition = getPos(code)
            
            if not platePosition.isdigit() or int(platePosition) < 1 or int(platePosition) > 12:
                print(f"Código inválido: {platePosition}")
                warnOccupiedPos(1)
                continue
                
            platePosition = int(platePosition)
            
            if isOccupied(platePosition):
                print(f"Posição {platePosition} ocupada!")
                warnOccupiedPos(platePosition)
                continue
                
            # Mostra azul para indicar posição correta (ETAPA 1)
            indicateRightPos(platePosition)
            print(f"Posição correta: {platePosition} (Azul)")
            
            # ETAPA 2: Aguarda pressionamento do switch correto
            while True:
                current_states = getSwitches()
                pressed_switches = [i+1 for i, state in enumerate(current_states) if state == 0]
                
                if platePosition in pressed_switches:
                    # Switch correto pressionado - mostra verde (ETAPA 2)
                    rightPos(platePosition)
                    togglePos(platePosition)
                    print("Posição confirmada! (Verde)")
                    break
                elif pressed_switches:
                    # Switch errado pressionado
                    wrong_pos = pressed_switches[0]
                    warnWrongPos(platePosition, wrong_pos)
                    print(f"ERRO: Posição {wrong_pos} pressionada!")
                    time.sleep(2)
                    indicateRightPos(platePosition)  # Volta para azul
                
                time.sleep(0.1)
            
            # ETAPA 3: Monitora se o switch é solto
            released = False
            while True:
                current_states = getSwitches()
                pressed_switches = [i+1 for i, state in enumerate(current_states) if state == 0]
                
                if platePosition not in pressed_switches:
                    # Switch foi solto - mostra vermelho (ETAPA 3)
                    if not released:
                        warnOccupiedPos(platePosition)
                        print("ERRO: Switch solto! (Vermelho)")
                        released = True
                else:
                    # Switch pressionado novamente após erro
                    if released:
                        # Mostra verde novamente quando pressionado após erro
                        rightPos(platePosition)
                        print("Correção confirmada! (Verde)")
                        # Aguarda soltar para finalizar
                        while platePosition in [i+1 for i, state in enumerate(getSwitches()) if state == 0]:
                            time.sleep(0.1)
                        break
                
                time.sleep(0.1)
            
            print("Operação concluída com sucesso!")
                
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