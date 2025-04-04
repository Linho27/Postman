#!/usr/bin/env python3 
# Sistema com resposta mais rápida ao pressionamento

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
            print(f"PS-{platePosition:03d}")  # Formato PS-007
            print(f"Posição correta: {platePosition} (Azul)")
            
            # ETAPA 2: Verificação mais rápida do switch
            last_print_time = time.time()
            while True:
                current_states = getSwitches()
                
                # Verificação mais direta e rápida
                if current_states[platePosition-1] == 0:  # Switch correto pressionado
                    rightPos(platePosition)
                    togglePos(platePosition)
                    print("Posição confirmada! (Verde)")
                    break
                
                # Feedback periódico da temperatura (sem atrasar o sistema)
                if time.time() - last_print_time > 2:  # A cada 2 segundos
                    print(f"Temperatura atual: {CPUTemperature().temperature:.2f}°C")
                    last_print_time = time.time()
                
                time.sleep(0.05)  # Verificação mais frequente (50ms)
            
            # ETAPA 3: Monitora se o switch é solto
            error_active = False
            while True:
                current_states = getSwitches()
                
                if current_states[platePosition-1] == 1 and not error_active:  # Switch solto
                    error_active = True
                    print("ERRO: Switch solto! (Vermelho piscante)")
                    
                    # Piscar vermelho em processo separado
                    def blink_red():
                        while error_active:
                            activate_segment(platePosition, RED)
                            time.sleep(0.3)
                            deactivate_segment(platePosition)
                            time.sleep(0.3)
                    
                    blink_process = multiprocessing.Process(target=blink_red)
                    blink_process.start()
                
                elif current_states[platePosition-1] == 0 and error_active:  # Pressionado novamente
                    error_active = False
                    blink_process.terminate()
                    rightPos(platePosition)
                    print("Switch pressionado novamente! (Verde)")
                    
                    # Aguarda soltar para finalizar
                    while getSwitches()[platePosition-1] == 0:
                        time.sleep(0.05)
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
        print("Sistema encerrado corretamente.")
        sys.exit(0)

if __name__ == "__main__":
    main()