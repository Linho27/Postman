import time
from modules.switches import getSwitches, compareSwitches, didntChange
from modules.fan import check_temp
from modules.leds import indicateRightPos, warnOccupiedPos, warnWrongPos, rightPos, ledsOff
from modules.connection import getPos, isOccupied, togglePos

def main():
    while True:
        print("A aguardar leitura do QR Code...")
        qr_code = input("Insere o código de série da peça: ").strip()
        
        if not qr_code:
            print("Código não pode estar vazio!")
            continue
        
        pos_correta = getPos(qr_code)
        if isinstance(pos_correta, str):
            print(pos_correta)  # Mensagem de erro
            continue
        
        if isOccupied(pos_correta):
            warnOccupiedPos(pos_correta)
            continue
        
        indicateRightPos(pos_correta)
        print("Coloca a peça na posição indicada.")
        time.sleep(2)
        
        estado_anterior = getSwitches()
        time.sleep(3)  # Tempo para o utilizador colocar a peça
        alteracoes = compareSwitches(estado_anterior)
        
        if didntChange(alteracoes):
            print("Nenhuma peça colocada. Tenta novamente.")
            ledsOff()
            continue
        
        if pos_correta in alteracoes:
            rightPos(pos_correta)
            togglePos(pos_correta)
        else:
            warnWrongPos(pos_correta, alteracoes[0])
            ledsOff()
        
        time.sleep(2)
        print("Processo concluído. A aguardar próximo código...")

if __name__ == "__main__":
    main()