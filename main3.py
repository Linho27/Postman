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
        
        # Estado inicial dos switches
        previous_states = getSwitches()
        
        while True:
            # Verificação de entrada de código (simulado)
            code = input("Aguardando leitura de código QR/Barra (ou digite 404 para sair): ").strip()
            
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
            switchesStates = getSwitches()
            while didntChange(compareSwitches(switchesStates)):
                time.sleep(0.5)
                
            ledsOff()  # Desligar LEDs de indicação
            
            # Verificar posicionamento final
            changed_switches = compareSwitches(switchesStates)
            positionIsRight = False
            
            while not positionIsRight:
                time.sleep(1)
                current_states = getSwitches()
                changed_switches = compareSwitches(switchesStates)
                
                if not changed_switches:  # Nenhuma mudança
                    continue
                    
                # Verificar se colocou na posição correta
                if (int(changed_switches[0]) + 1) == platePosition:
                    print("Placa colocada na posição correta!")
                    rightPos(platePosition)
                    togglePos(platePosition)  # Atualizar estado na API
                    positionIsRight = True
                else:
                    print(f"Placa colocada na posição errada! (Posição {changed_switches[0] + 1})")
                    warnWrongPos(platePosition, changed_switches[0] + 1)
                    
                switchesStates = current_states  # Atualizar estado para próxima verificação

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