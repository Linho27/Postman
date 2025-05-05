# Sistema com feedback vermelho piscante até novo pressionamento

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
        
        # Teste inicial dos LEDs
        startUpLEDS()
        
        while True:
            # ETAPA 1: Leitura do código
            previous_states = getSwitches()
            code = input("Aguardando leitura de código (ou digite 404 para sair): ").strip()
            
            syncSwitchesWithAPI()

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
            print(f"Posição correta: {platePosition} (Azul)")
            
            # ETAPA 2: Aguarda pressionamento correto
            while True:
                current_states = getSwitches()
                pressed_switches = [i+1 for i, state in enumerate(current_states) if state == 0]
                
                if platePosition in pressed_switches:
                    # Switch correto pressionado - mostra verde
                    rightPos(platePosition)
                    togglePos(platePosition)
                    print("Posição confirmada! (Verde)")
                    break
                elif pressed_switches:
                    # Switch errado pressionado
                    wrong_pos = pressed_switches[0]
                    warnWrongPos(platePosition, wrong_pos)
                    print(f"ERRO: Posição {wrong_pos} pressionada!")
                    time.sleep(2)
                    indicateRightPos(platePosition)  # Volta para azul
                
                time.sleep(0.1)
            
            # ETAPA 3: Monitora se o switch é solto
            error_active = False
            while True:
                current_states = getSwitches()
                pressed_switches = [i+1 for i, state in enumerate(current_states) if state == 0]
                
                if platePosition not in pressed_switches and not error_active:
                    # Switch foi solto - começa a piscar vermelho infinitamente
                    error_active = True
                    print("ERRO: Switch solto! (Vermelho piscante)")
                    
                    # Processo para piscar infinitamente
                    def blink_red():
                        while error_active:
                            activate_segment(platePosition, RED)
                            time.sleep(0.5)
                            deactivate_segment(platePosition)
                            time.sleep(0.5)
                    
                    blink_process = multiprocessing.Process(target=blink_red)
                    blink_process.start()
                
                elif platePosition in pressed_switches and error_active:
                    # Switch pressionado novamente após erro - para de piscar e mostra verde
                    error_active = False
                    blink_process.terminate()
                    rightPos(platePosition)
                    print("Switch pressionado novamente! (Verde)")
                    
                    # Aguarda soltar para finalizar
                    while platePosition in [i+1 for i, state in enumerate(getSwitches()) if state == 0]:
                        time.sleep(0.1)
                    break
                
                time.sleep(0.1)
            
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