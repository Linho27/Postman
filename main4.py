#!/usr/bin/env python3 
# Sistema com múltiplos códigos e verificação simultânea

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
        
        # Dicionário para armazenar códigos escaneados e suas posições
        scanned_codes = {}
        
        while True:
            # Modo de escaneamento
            print("\nModo de escaneamento - digite 'fim' para terminar")
            while True:
                code = input("Escanear código QR/Barra (ou 'fim' para verificação): ").strip()
                
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
                    print(f"Código inválido ou placa não encontrada: {platePosition}")
                    continue
                    
                platePosition = int(platePosition)
                
                if isOccupied(platePosition):
                    print(f"Posição {platePosition} já está ocupada!")
                    continue
                
                scanned_codes[code] = platePosition
                print(f"Código {code} - Posição {platePosition} adicionado")
                indicateRightPos(platePosition)  # Mostra azul para cada posição escaneada
            
            # ETAPA DE VERIFICAÇÃO
            print("\nIniciando verificação de switches...")
            required_positions = list(scanned_codes.values())
            print(f"Posições requeridas: {required_positions}")
            
            # Variáveis de controle
            all_confirmed = False
            error_processes = []
            
            while not all_confirmed:
                current_states = getSwitches()
                pressed_switches = [i+1 for i, state in enumerate(current_states) if state == 0]
                
                # Verifica se todos os requeridos estão pressionados
                if all(pos in pressed_switches for pos in required_positions):
                    if not all_confirmed:
                        # Confirma todas as posições
                        for pos in required_positions:
                            rightPos(pos)
                            togglePos(pos)
                        print("Todas as posições confirmadas! (Verde)")
                        all_confirmed = True
                
                # Verifica se algum required foi solto após confirmação
                elif all_confirmed and any(pos not in pressed_switches for pos in required_positions):
                    print("ERRO: Alguma posição foi solta! (Vermelho piscante)")
                    
                    # Inicia piscar vermelho para as posições soltas
                    for pos in required_positions:
                        if pos not in pressed_switches:
                            def blink_red(pos):
                                while True:
                                    activate_segment(pos, RED)
                                    time.sleep(0.3)
                                    deactivate_segment(pos)
                                    time.sleep(0.3)
                            
                            p = multiprocessing.Process(target=blink_red, args=(pos,))
                            p.start()
                            error_processes.append(p)
                    
                    # Aguarda re-pressionamento
                    while not all(pos in [i+1 for i, state in enumerate(getSwitches()) if state == 0] 
                               for pos in required_positions):
                        time.sleep(0.1)
                    
                    # Para os processos de erro e reconfirma
                    for p in error_processes:
                        p.terminate()
                    error_processes = []
                    
                    for pos in required_positions:
                        rightPos(pos)
                    print("Todas as posições pressionadas novamente! (Verde)")
                
                # Verifica posições erradas pressionadas
                wrong_positions = [pos for pos in pressed_switches if pos not in required_positions]
                if wrong_positions:
                    for pos in required_positions:
                        warnWrongPos(pos, wrong_positions)
                    print(f"ERRO: Posições incorretas pressionadas: {wrong_positions}")
                    time.sleep(2)
                    for pos in required_positions:
                        indicateRightPos(pos)  # Volta para azul
                
                time.sleep(0.1)
            
            # Espera até todos serem soltos para finalizar
            print("Aguardando soltar todos os switches...")
            while any(state == 0 for state in getSwitches()):
                time.sleep(0.1)
            
            print("Operação concluída com sucesso!")
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