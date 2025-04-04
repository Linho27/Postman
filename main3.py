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
            while True:
                switchesStates = getSwitches()
                changed_switches = compareSwitches(previous_states)
                
                if changed_switches:  # Se houve mudança nos switches
                    if (int(changed_switches[0]) + 1) == platePosition:
                        print("Placa colocada na posição correta!")
                        rightPos(platePosition)
                        togglePos(platePosition)  # Atualizar estado na API
                        
                        # Agora garantimos que a posição continua pressionada
                        while getSwitches()[platePosition - 1] == 0:
                            time.sleep(0.5)  # Espera enquanto o switch está pressionado
                        
                        # Quando o switch é solto, continua a dar erro até ser pressionado novamente
                        print("Switch solto! Erro até ser pressionado novamente.")
                        warnOccupiedPos(platePosition)
                        while getSwitches()[platePosition - 1] == 1:
                            time.sleep(0.5)  # Aguarda até o switch ser pressionado novamente
                        
                        print("Switch pressionado novamente! Pode continuar.")
                        break  # Sai do loop para pedir um novo código
                    else:
                        print(f"Placa colocada na posição errada! (Posição {changed_switches[0] + 1})")
                        warnWrongPos(platePosition, changed_switches[0] + 1)
                        break  # Sai do loop para pedir um novo código
                
                time.sleep(0.5)  # Pequeno atraso para evitar sobrecarga
                
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
