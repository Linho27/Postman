#!/usr/bin/env python3  
# Sistema com múltiplos códigos, verificação por etapas e monitoramento de integridade

from modules.fan import *
from modules.leds import *
from modules.switches import *
from modules.connection import *
import RPi.GPIO as GPIO                     # type: ignore
import multiprocessing
import time
import sys

def monitorar_integridade(posicoes_verificadas, flag):
    while flag.is_set():
        current_states = getSwitches()
        removidas = [pos for pos in posicoes_verificadas if current_states[pos-1] == 1]
        
        if len(removidas) >= 2:  # Se 2 ou mais forem removidas
            print(f"\n⚠️ ALERTA: Várias peças foram removidas! ({removidas})")
            # Piscar vermelho nas posições afetadas
            while any(getSwitches()[pos-1] == 1 for pos in removidas):
                for pos in removidas:
                    activate_segment(pos, RED)
                time.sleep(0.3)
                for pos in removidas:
                    deactivate_segment(pos)
                time.sleep(0.3)
            # Quando forem recolocadas, reativa o verde
            for pos in removidas:
                rightPos(pos)
            print("✅ Peças recolocadas. Monitoramento retomado.")
        time.sleep(0.1)

def main():
    try:
        print("Sistema de gerenciamento de placas iniciando...")
        
        # Controle de temperatura
        tempChecking = multiprocessing.Process(target=check_temp, daemon=True)
        tempChecking.start()
        
        # Teste inicial dos LEDs
        startUp()
        
        scanned_codes = {}
        
        while True:
            # FASE 1: Modo de escaneamento automático até completar 12 ou pressionar posição
            print("\nModo de escaneamento - pressione qualquer posição para iniciar verificação")
            while True:
                current_states = getSwitches()
                pressed_switches = [i+1 for i, state in enumerate(current_states) if state == 0]
                
                if pressed_switches and scanned_codes:
                    print("Iniciando verificação...")
                    time.sleep(0.3)
                    break
                
                if len(scanned_codes) == 12:
                    print("12 posições escaneadas automaticamente.")
                    break
                
                try:
                    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                        code = sys.stdin.readline().strip()
                    else:
                        time.sleep(0.1)
                        continue
                except:
                    code = input("Escanear código QR/Barra: ").strip()
                
                if not code:
                    continue
                
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
            
            # FASE 2: Verificação por etapas
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
                        
                        # FASE 2.2: Monitora se é solto
                        while True:
                            current_states = getSwitches()
                            if current_states[current_pos - 1] == 1:
                                print("ERRO: Switch solto! (Vermelho piscante)")
                                while getSwitches()[current_pos - 1] == 1:
                                    activate_segment(current_pos, RED)
                                    time.sleep(0.3)
                                    deactivate_segment(current_pos)
                                    time.sleep(0.3)
                                rightPos(current_pos)
                                print("Switch pressionado novamente! (Verde)")
                                break
                            time.sleep(0.1)
                        
                        remaining_positions.pop(0)
                        break
                    
                    # Verifica se pressionou posição errada
                    wrong_positions = [pos for pos in pressed_switches if pos in remaining_positions and pos != current_pos]
                    if wrong_positions:
                        warnWrongPos(current_pos, wrong_positions)
                        print(f"ERRO: Posição errada pressionada: {wrong_positions}")
                        time.sleep(2)
                        indicateRightPos(current_pos)
                    
                    time.sleep(0.1)
            
            print("\n✅ Todas as posições verificadas com sucesso!")
            
            # FASE 3: Monitoramento contínuo de integridade
            print("⏱️ Iniciando monitoramento de integridade...")
            monitor_flag = multiprocessing.Event()
            monitor_flag.set()
            monitor_proc = multiprocessing.Process(
                target=monitorar_integridade,
                args=(list(scanned_codes.values()), monitor_flag),
                daemon=True
            )
            monitor_proc.start()
            
            # Espera até novo escaneamento para resetar
            input("\nPressione ENTER para novo escaneamento...\n")
            monitor_flag.clear()
            monitor_proc.terminate()
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
