#!/usr/bin/env python3 
# Sistema com detecção automática sem select.select

from modules.fan import *
from modules.leds import *
from modules.switches import *
from modules.connection import *
import RPi.GPIO as GPIO                     # type: ignore
import multiprocessing
import time
import sys
import fcntl
import os

def set_non_blocking(fd):
    """Configura um file descriptor para non-blocking"""
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

def main():
    try:
        # Configura stdin para non-blocking
        set_non_blocking(sys.stdin.fileno())
        
        # Inicialização
        print("Sistema de gerenciamento iniciando...")
        tempChecking = multiprocessing.Process(target=check_temp, daemon=True)
        tempChecking.start()
        startUp()
        
        scanned_positions = []
        blink_processes = []
        
        while True:
            # Modo de escaneamento ativo
            print("\nModo de escaneamento ativo")
            print("Pressione todos os switches escaneados para verificação")
            
            while True:
                # Verifica se todos os escaneados estão pressionados
                current_states = getSwitches()
                pressed = [i+1 for i, state in enumerate(current_states) if state == 0]
                
                if scanned_positions and all(pos in pressed for pos in scanned_positions):
                    print("Todos os switches escaneados pressionados! Iniciando verificação...")
                    time.sleep(0.5)  # Debounce
                    break
                
                # Verifica novo código (non-blocking)
                try:
                    code = sys.stdin.readline().strip()
                    if code:
                        pos = getPos(code)
                        
                        if not pos.isdigit() or int(pos) < 1 or int(pos) > 12:
                            print(f"Código inválido: {pos}")
                            continue
                            
                        pos = int(pos)
                        
                        if pos in scanned_positions:
                            print(f"Posição {pos} já escaneada!")
                            continue
                            
                        if isOccupied(pos):
                            print(f"Posição {pos} ocupada!")
                            continue
                            
                        scanned_positions.append(pos)
                        indicateRightPos(pos)
                        print(f"PS-{pos:03d} adicionado. Posições ativas: {scanned_positions}")
                except IOError:
                    pass  # Não há input disponível
                
                time.sleep(0.1)
            
            # Fase de verificação
            print("\nFase de verificação iniciada")
            
            for pos in scanned_positions.copy():
                print(f"\nVerificando posição {pos}...")
                indicateRightPos(pos)
                
                confirmed = False
                while not confirmed:
                    current_states = getSwitches()
                    pressed = [i+1 for i, state in enumerate(current_states) if state == 0]
                    
                    if pos in pressed:
                        rightPos(pos)
                        togglePos(pos)
                        print("Posição confirmada! (Verde)")
                        
                        # Monitora se é solto
                        while True:
                            current_states = getSwitches()
                            if pos not in [i+1 for i, state in enumerate(current_states) if state == 0]:
                                # Pisca vermelho até pressionar novamente
                                print("ERRO: Switch solto! (Vermelho piscante)")
                                p = multiprocessing.Process(target=blink_segment, args=(pos, RED, 0, 0))
                                p.start()
                                blink_processes.append(p)
                                
                                while pos not in [i+1 for i, state in enumerate(getSwitches()) if state == 0]:
                                    time.sleep(0.1)
                                
                                for p in blink_processes:
                                    p.terminate()
                                blink_processes = []
                                
                                rightPos(pos)
                                print("Correção confirmada! (Verde)")
                            else:
                                break
                            time.sleep(0.1)
                        
                        scanned_positions.remove(pos)
                        confirmed = True
                        break
                    
                    time.sleep(0.1)
            
            print("\nTodas as posições verificadas com sucesso!")
            scanned_positions = []
            
    except KeyboardInterrupt:
        print("\nPrograma interrompido")
    except Exception as e:
        print(f"Erro: {str(e)}")
    finally:
        GPIO.cleanup()
        ledsOff()
        for p in multiprocessing.active_children():
            p.terminate()
        print("Sistema encerrado")

if __name__ == "__main__":
    main()