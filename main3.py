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

def main():
    try:
        # Inicialização do sistema
        print("Sistema de gerenciamento de placas iniciando...")
        
        # Controle de temperatura em processo separado
        tempChecking = multiprocessing.Process(target=check_temp, daemon=True)
        tempChecking.start()
        
        # Teste inicial dos LEDs
        startUp()
        
        while True:
            # Estado inicial dos switches
            previous_states = getSwitches()
            
            # Verificação de entrada de código (simulado)
            code = input("Aguardando leitura de código QR/Barra (ou digite 404 para sair): ").strip()
            
            syncSwitchesWithAPI()

            if code == '404':
                break
                
            # Obter posição correta da placa
            platePosition = getPos(code)
            
            # Verificar se o código é válido
            if not platePosition.isdigit() or int(platePosition) < 1 or int(platePosition) > 12:
                print(f"Código inválido ou placa não encontrada: {platePosition}")
                warnOccupiedPos(1)  # Usa posição 1 como padrão para erro
                continue
                
            platePosition = int(platePosition)
            
            # Verificar se a posição está ocupada
            if isOccupied(platePosition):
                print(f"Posição {platePosition} está ocupada!")
                warnOccupiedPos(platePosition)
                continue
                
            # Indicar posição correta
            indicateRightPos(platePosition)
            
            # Monitorar mudanças nos switches
            pressed_switches = []
            while True:
                current_states = getSwitches()
                changed_switches = compareSwitches(previous_states)
                
                # Verifica se houve mudança nos switches
                if changed_switches:
                    # Obtém as posições dos switches pressionados (1-12)
                    pressed_switches = [i+1 for i, state in enumerate(current_states) if state == 0]
                    
                    # Verifica se a posição correta está entre os pressionados
                    if platePosition in pressed_switches:
                        print("Placa colocada na posição correta!")
                        rightPos(platePosition)
                        togglePos(platePosition)  # Atualizar estado na API
                        
                        # Espera até que todos os switches sejam soltos
                        while any(state == 0 for state in getSwitches()):
                            time.sleep(0.1)
                        
                        print("Todos os switches soltos! Aguardando novo código.")
                        break
                    else:
                        # Mostra erro para todas as posições erradas pressionadas
                        print(f"Placa colocada na posição(ões) errada(s): {pressed_switches}")
                        warnWrongPos(platePosition, pressed_switches)
                        break
                
                # Verifica se todos os switches foram soltos após terem sido pressionados
                if len(pressed_switches) > 0 and all(state == 1 for state in current_states):
                    print("Todos os switches soltos após pressionados! Erro.")
                    warnOccupiedPos(platePosition)
                    break
                
                previous_states = current_states
                time.sleep(0.1)  # Pequeno atraso para evitar sobrecarga
                
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