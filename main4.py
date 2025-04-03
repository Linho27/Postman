from modules.switches import switch_manager
from modules.fan import *
from modules.leds import *
from modules.connection import *
import multiprocessing
import atexit
import sys

def safe_exit():
    """Função de encerramento seguro"""
    print("\nExecutando limpeza final...")
    switch_manager.cleanup()
    ledsOff()
    sys.exit(0)

def main():
    try:
        # Registra handler para Ctrl+C e término normal
        atexit.register(safe_exit)
        
        # Inicialização
        print("=== Sistema Iniciando ===")
        startUp()  # Teste dos LEDs
        
        # Controle de temperatura em processo separado
        temp_process = multiprocessing.Process(target=check_temp, daemon=True)
        temp_process.start()
        
        # Sincronização inicial
        print("Sincronizando switches com API...")
        switch_manager.syncSwitchesWithAPI()
        
        # Loop principal
        while True:
            # Sua lógica principal aqui
            time.sleep(1)
            
    except Exception as e:
        print(f"ERRO: {str(e)}")
        safe_exit()

if __name__ == "_main_":
    main()