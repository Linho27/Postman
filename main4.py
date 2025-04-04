#!/usr/bin/env python3 
# Sistema com múltiplos switches simultâneos

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
            # ETAPA 1: Leitura do código
            code = input("Aguardando leitura de código (ou digite 404 para sair): ").strip()
            
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
                
            # ETAPA 1: Mostra azul para indicar posição correta
            indicateRightPos(platePosition)
            print(f"PS-{platePosition:03d}")
            print(f"Posição correta: {platePosition} (Azul)")
            
            # ETAPA 2: Verificação rápida dos switches
            correct_confirmed = False
            blink_processes = []
            
            while True:
                current_states = getSwitches()
                pressed_switches = [i+1 for i, state in enumerate(current_states) if state == 0]
                
                # Verifica se o switch correto está pressionado
                if platePosition in pressed_switches and not correct_confirmed:
                    correct_confirmed = True
                    rightPos(platePosition)
                    togglePos(platePosition)
                    print("Posição confirmada! (Verde)")
                
                # Verifica switches errados pressionados
                wrong_switches = [pos for pos in pressed_switches if pos != platePosition]
                if wrong_switches:
                    warnWrongPos(platePosition, wrong_switches)
                    print(f"ERRO: Posições erradas pressionadas: {wrong_switches}")
                
                # ETAPA 3: Tratamento quando solto após confirmação
                if correct_confirmed and platePosition not in pressed_switches:
                    print("ERRO: Switch solto! (Vermelho piscante)")
                    
                    # Inicia piscar vermelho para cada posição necessária
                    for pos in [platePosition] + wrong_switches:
                        def blink_red(pos):
                            while True:
                                activate_segment(pos, RED)
                                time.sleep(0.3)
                                deactivate_segment(pos)
                                time.sleep(0.3)
                        
                        p = multiprocessing.Process(target=blink_red, args=(pos,))
                        p.start()
                        blink_processes.append(p)
                    
                    # Aguarda re-pressionamento
                    while platePosition not in [i+1 for i, state in enumerate(getSwitches()) if state == 0]:
                        time.sleep(0.05)
                    
                    # Para todos os processos de piscar
                    for p in blink_processes:
                        p.terminate()
                    blink_processes = []
                    
                    rightPos(platePosition)
                    print("Switch pressionado novamente! (Verde)")
                    correct_confirmed = False  # Reinicia o ciclo
                
                # Condição de saída - quando solto após confirmação final
                if correct_confirmed and not any([i+1 for i, state in enumerate(getSwitches()) if state == 0]):
                    break
                
                time.sleep(0.05)
            
            print("Operação concluída com sucesso!")
                
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
    finally:
        GPIO.cleanup()
        ledsOff()
        # Garante que todos os processos de piscar sejam terminados
        for p in multiprocessing.active_children():
            if p != tempChecking:
                p.terminate()
        print("Sistema encerrado corretamente.")
        sys.exit(0)

if __name__ == "__main__":
    main()