from modules.leds import *
from modules.switches import getSwitches
from modules.connection import getPos, togglePos, isOccupied
import RPi.GPIO as GPIO
import time
import sys

def main():
    try:
        print("=== Sistema de Teste de Placas ===")
        ledsOff()
        startUpLEDS()

        while True:
            code = input("\nEscaneie ou insira o código da placa (ou 'sair' para terminar): ").strip()
            if code.lower() == 'sair':
                break
            if not code:
                continue

            # Obter posição da placa via API
            pos = getPos(code)
            if isinstance(pos, str):
                print(pos)
                continue
            try:
                pos = int(pos)
            except Exception:
                print("Erro ao converter posição recebida da API.")
                continue
            if pos < 1 or pos > 12:
                print("Posição inválida (fora do intervalo 1-12).")
                continue

            indicateRightPos(pos)
            print(f"Coloque a placa na posição {pos} e pressione o switch correspondente.")

            while True:
                states = getSwitches()
                pressed = [i+1 for i, s in enumerate(states) if s == 0]
                if pressed:
                    if pos in pressed:
                        deactivate_segment(pos)
                        rightPos(pos)
                        print("Posição correta! (Verde)")
                        togglePos(pos)
                        ledsOff()
                        break
                    else:
                        for p in pressed:
                            blink_segment(p, RED)
                        blink_segment(pos, YELLOW)
                        print(f"ERRO: Switch errado pressionado: {pressed}. Remova a placa errada.")
                        # Espera até todos os switches errados serem libertados
                        while True:
                            states = getSwitches()
                            still_wrong = [p for p in pressed if states[p-1] == 0]
                            if not still_wrong:
                                break
                            time.sleep(0.1)
                        indicateRightPos(pos)
                time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo utilizador.")
    except Exception as e:
        print(f"Erro inesperado: {e}")
    finally:
        GPIO.cleanup()
        ledsOff()
        print("Sistema encerrado corretamente.")
        sys.exit(0)

if __name__ == "__main__":
    main()
