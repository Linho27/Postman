#!/usr/bin/env python3 
# Sistema com múltiplos códigos e verificação por etapas

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
        
        # Dicionário para armazenar códigos escaneados
        scanned_codes = {}
        
        while True:
            # FASE 1: Modo de escaneamento
            print("\nModo de escaneamento - digite 'fim' para verificação")
            while True:
                code = input("Escanear código QR/Barra: ").strip()
                
                if code.lower() == 'fim':
                    if not scanned_codes:
                        print("Nenhum código escaneado!")
                        continue
                    break
                
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
                indicateRightPos(platePosition)  # Mostra azul para posição escaneada
            
            # FASE 2: Verificação por etapas
            print("\nIniciando verificação por etapas...")
            remaining_positions = list(scanned_codes.values())
            error_processes = []
            
            while remaining_positions:
                current_pos = remaining_positions[0]
                print(f"\nVerificando posição {current_pos}...")
                
                # Mostra azul para posição atual
                indicateRightPos(current_pos)
                
                # FASE 2.1: Aguarda pressionamento correto
                pressed = False
                while not pressed:
                    current_states = getSwitches()
                    pressed_switches = [i+1 for i, state in enumerate(current_states) if state == 0]
                    
                    if current_pos in pressed_switches:
                        pressed = True
                        rightPos(current_pos)  # Verde
                        togglePos(current_pos)
                        print("Posição confirmada! (Verde)")
                        
                        # FASE 2.2: Monitora se é solto
                        released = False
                        while True:
                            current_states = getSwitches()
                            if current_pos not in [i+1 for i, state in enumerate(current_states) if state == 0]:
                                released = True
                                warnOccupiedPos(current_pos)  # Vermelho piscante
                                print("ERRO: Switch solto! (Vermelho)")
                                
                                # FASE 2.3: Aguarda pressionamento novamente
                                while current_pos not in [i+1 for i, state in enumerate(getSwitches()) if state == 0]:
                                    time.sleep(0.1)
                                
                                rightPos(current_pos)  # Verde novamente
                                print("Switch pressionado novamente! (Verde)")
                            elif released:
                                break
                            time.sleep(0.1)
                        
                        # Remove da lista quando confirmado e solto
                        remaining_positions.pop(0)
                        break
                    
                    # Verifica se pressionou posição errada
                    wrong_positions = [pos for pos in pressed_switches if pos in remaining_positions and pos != current_pos]
                    if wrong_positions:
                        warnWrongPos(current_pos, wrong_positions)
                        print(f"ERRO: Posição errada pressionada: {wrong_positions}")
                        time.sleep(2)
                        indicateRightPos(current_pos)  # Volta para azul
                    
                    time.sleep(0.1)
            
            print("\nTodas as posições verificadas com sucesso!")
            scanned_codes = {}  # Reseta para nova operação
            
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
    finally:
        GPIO.cleanup()
        ledsOff()
        # Termina todos os processos
        for p in multiprocessing.active_children():
            p.terminate()
        print("Sistema encerrado corretamente.")
        sys.exit(0)

if __name__ == "__main__":
    main()