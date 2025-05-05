import time
from modules.switches import getSwitches, compareSwitches, didntChange
from modules.leds import indicateRightPos, warnOccupiedPos, warnWrongPos, rightPos, ledsOff
from modules.connection import getPos, isOccupied, togglePos

def main():
    while True:
        print("A aguardar leitura do QR Code...")
        qr_code = input("Insere o código de série da peça: ").strip()
        
        if not qr_code:
            print("Erro: Código não pode estar vazio!")
            continue
        
        print(f"Código inserido: {qr_code}")
        pos_correta = getPos(qr_code)
        print(f"Posição obtida: {pos_correta}")
        
        if isinstance(pos_correta, str):
            print(f"Erro ao obter posição: {pos_correta}")
            continue
        
        if isOccupied(pos_correta):
            print(f"Posição {pos_correta} ocupada!")
            warnOccupiedPos(pos_correta)
            continue
        
        print(f"Posição {pos_correta} está livre. Indicando posição com LEDs.")
        indicateRightPos(pos_correta)
        print("Coloca a peça na posição indicada.")
        time.sleep(2)
        
        estado_anterior = getSwitches()
        time.sleep(3)  # Tempo para o utilizador colocar a peça
        alteracoes = compareSwitches(estado_anterior)
        print(f"Alterações detectadas: {alteracoes}")
        
        if didntChange(alteracoes):
            print("Nenhuma peça colocada. Tenta novamente.")
            ledsOff()
            continue
        
        if pos_correta in alteracoes:
            print(f"Peça colocada corretamente na posição {pos_correta}.")
            rightPos(pos_correta)
            togglePos(pos_correta)
        else:
            print(f"Peça colocada na posição errada: {alteracoes[0]} (esperado {pos_correta}).")
            warnWrongPos(pos_correta, alteracoes[0])
            ledsOff()
        
        time.sleep(2)
        print("Processo concluído. A aguardar próximo código...")

if __name__ == "__main__":
    main()