#!/usr/bin/env python3 
# Sistema completo com feedback visual aprimorado para múltiplos switches

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
            
            # Verificação de entrada de código
            code = input("Aguardando leitura de código QR/Barra (ou digite 404 para sair): ").strip()
            
            syncSwitchesWithAPI()

            if code == '404':
                break
                
            # Obter posição correta da placa
            platePosition = getPos(code)
            
            # Verificar se o código é válido
            if not platePosition.isdigit() or int(platePosition) < 1 or int(platePosition) > 12:
                print(f"Código inválido ou placa não encontrada: {platePosition}")
                warnOccupiedPos(1)
                continue
                
            platePosition = int(platePosition)
            
            # Verificar se a posição está ocupada
            if isOccupied(platePosition):
                print(f"Posição {platePosition} está ocupada!")
                warnOccupiedPos(platePosition)
                continue
                
            # Indicar posição correta
            indicateRightPos(platePosition)
            
            # Variáveis de estado
            first_press = True
            correct_confirmed = False
            
            while True:
                current_states = getSwitches()
                pressed_switches = [i+1 for i, state in enumerate(current_states) if state == 0]
                
                # Primeira pressão correta
                if platePosition in pressed_switches and first_press:
                    print("Posição correta pressionada pela primeira vez!")
                    rightPos(platePosition)
                    togglePos(platePosition)
                    first_press = False
                    correct_confirmed = True
                    
                    # Espera até soltar
                    while platePosition in [i+1 for i, state in enumerate(getSwitches()) if state == 0]:
                        time.sleep(0.1)
                    
                    print("Switch solto! Aguardando segunda pressão...")
                    indicateRightPos(platePosition)  # Volta para azul
                
                # Segunda pressão após soltar
                elif platePosition in pressed_switches and not first_press and correct_confirmed:
                    print("Posição correta pressionada novamente!")
                    activate_segment(platePosition, GREEN)  # Verde imediatamente
                    time.sleep(2)  # Mantém verde por 2 segundos
                    
                    # Espera até soltar para finalizar
                    while platePosition in [i+1 for i, state in enumerate(getSwitches()) if state == 0]:
                        time.sleep(0.1)
                    
                    print("Operação concluída com sucesso!")
                    break
                
                # Tratamento de erros
                elif pressed_switches:
                    # Pressionou posição errada
                    wrong_positions = [pos for pos in pressed_switches if pos != platePosition]
                    if wrong_positions:
                        print(f"Posições erradas pressionadas: {wrong_positions}")
                        warnWrongPos(platePosition, wrong_positions)
                
                # Todos switches soltos após erro
                elif not pressed_switches and not first_press and not correct_confirmed:
                    print("ERRO: Switch solto antes da confirmação!")
                    warnOccupiedPos(platePosition)
                    break
                
                time.sleep(0.1)
                
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