#!/usr/bin/env python3 
# Sistema com múltiplos códigos e verificação por etapas (pisca vermelho até voltar a pressionar)

from modules.fan import *
from modules.leds import *
from modules.switches import *
from modules.connection import *
import RPi.GPIO as GPIO                     # type: ignore
import multiprocessing
import time
import sys
import select

def piscar_vermelho(pos, flag):
    while flag.is_set():
        activate_segment(pos, RED)
        time.sleep(0.3)
        deactivate_segment(pos)
        time.sleep(0.3)

def main():
    try:
        print("Sistema de gerenciamento de placas iniciando...")
        
        tempChecking = multiprocessing.Process(target=check_temp, daemon=True)
        tempChecking.start()
        
        startUp()
        
        scanned_codes = {}
        
        while True:
            print("\nModo de escaneamento (pressione todos os switches para iniciar verificação)")
            while True:
                current_states = getSwitches()
                pressed_positions = [i+1 for i, state in enumerate(current_states) if state == 0]
                
                if scanned_codes and all(pos in pressed_positions for pos in scanned_codes.values()):
                    print("Todos os switches escaneados pressionados! Iniciando verificação...")
                    time.sleep(0.5)
                    break

                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    code = sys.stdin.readline().strip()
                    
                    if not code or code in scanned_codes:
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
                
                time.sleep(0.1)

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
                        
                        # Monitorar se é solto e piscar vermelho até pressionar novamente
                        released_flag = multiprocessing.Event()
                        released_flag.set()
                        blink_proc = multiprocessing.Process(target=piscar_vermelho, args=(current_pos, released_flag))
                        
                        while True:
                            current_states = getSwitches()
                            pressed_now = [i+1 for i, state in enumerate(current_states) if state == 0]
                            
                            if current_pos not in pressed_now:
                                print("ERRO: Switch solto! (Vermelho piscante)")
                                blink_proc.start()
                                
                                while current_pos not in [i+1 for i, state in enumerate(getSwitches()) if state == 0]:
                                    time.sleep(0.1)
                                
                                released_flag.clear()
                                blink_proc.terminate()
                                rightPos(current_pos)
                                print("Switch pressionado novamente! (Verde)")
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
            scanned_codes = {}
    
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
