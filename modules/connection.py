#API connection module

# Libraries import
import requests


linkAPI = "http://127.0.0.1:5000"
def getPos(id):
    # Definir a URL do servidor Flask
    url = linkAPI + f'/todas_as_pecas'

    try:
        # Fazer a requisição GET para obter todas as peças
        resposta = requests.get(url)
        
        # Se a resposta for bem-sucedida (status code 200)
        if resposta.status_code == 200:
            pecas = resposta.json()
            
            # Procurar a peça pelo número de série
            for numero, dados in pecas.items():
                if dados["numero_serie"] == id:
                    return numero  # Devolver a posição (número) da peça
            return f"Peça com código de série {id} não encontrada."
        else:
            return f"Erro ao obter dados do servidor. Código de status: {resposta.status_code}"
    
    except requests.exceptions.RequestException as e:
        return f"Erro na requisição: {e}"
    
def isOccupied(pos):
    url = linkAPI + f"/estado/{pos}"
    
    try:
        # Send GET request to the API
        resposta = requests.get(url)
        
        # Verify if answer was successful
        if resposta.status_code == 200:
            estado = resposta.json()
            
            # Verifica o estado do número e retorna True se for "ocupado"
            return estado.get(str(pos)) == "ocupado"
        else:
            print(f"Erro na requisição: {resposta.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Erro na conexão com a API: {e}")
        return False
