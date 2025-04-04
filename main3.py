#!/usr/bin/env python3 
# Sistema completo de gerenciamento de placas com múltiplos switches simultâneos

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
            
            # Variáveis para controle de estado
            correct_pressed = False
            required_switches = [platePosition]  # Pode ser expandido para múltiplas posições necessárias
            pressed_history = []
            
            # Monitorar mudanças nos switches
            while True:
                current_states = getSwitches()
                pressed_switches = [i+1 for i, state in enumerate(current_states) if state == 0]
                
                # Verifica se todos os switches necessários estão pressionados
                if all(pos in pressed_switches for pos in required_switches):
                    if not correct_pressed:
                        print("Todos os switches necessários pressionados corretamente!")
                        rightPos(platePosition)
                        togglePos(platePosition)
                        correct_pressed = True
                    
                    # Monitora se algum switch necessário foi solto
                    if any(pos not in pressed_switches for pos in required_switches):
                        print("ERRO: Switch necessário foi solto!")
                        for pos in required_switches:
                            if pos not in pressed_switches:
                                blink_segment(pos, RED, duration=0.5, blinks=1)
                
                # Verifica se switches errados foram pressionados
                wrong_switches = [pos for pos in pressed_switches if pos not in required_switches]
                if wrong_switches and wrong_switches != pressed_history:
                    print(f"Switches errados pressionados: {wrong_switches}")
                    warnWrongPos(platePosition, wrong_switches)
                
                # Verifica se todos os switches foram soltos após terem sido pressionados
                if not pressed_switches and pressed_history:
                    print("ERRO: Todos os switches foram soltos!")
                    warnOccupiedPos(platePosition)
                    break
                
                # Atualiza histórico e espera próxima verificação
                pressed_history = pressed_switches.copy()
                time.sleep(0.1)
                
                # Condição de saída quando correto e solto
                if correct_pressed and not pressed_switches:
                    print("Operação concluída com sucesso!")
                    break
                    
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