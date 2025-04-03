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
 # Verificação de entrada de código (simulado)
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
            
            # Monitorar mudanças nos switches
            switchesStates = getSwitches()
            while didntChange(compareSwitches(switchesStates)):
                time.sleep(0.5)
                
            ledsOff()  # Desligar LEDs de indicação
            
            # Verificar posicionamento final
            changed_switches = compareSwitches(switchesStates)
            positionIsRight = False
            
            while not positionIsRight:
                time.sleep(1)
                current_states = getSwitches()
                changed_switches = compareSwitches(switchesStates)
                
                if not changed_switches:  # Nenhuma mudança
                    continue
                    
                # Verificar se colocou na posição correta
                if (int(changed_switches[0]) + 1) == platePosition:
                    print("Placa colocada na posição correta!")
                    rightPos(platePosition)
                    togglePos(platePosition)  # Atualizar estado na API
                    positionIsRight = True
                else:
                    print(f"Placa colocada na posição errada! (Posição {changed_switches[0] + 1})")
                    warnWrongPos(platePosition, changed_switches[0] + 1)
                    
                switchesStates = current_states  # Atualizar estado para próxima verificação            # Sua lógica principal aqui
            time.sleep(1)
            
    except Exception as e:
        print(f"ERRO: {str(e)}")
        safe_exit()

if __name__ == "_main_":
    main()