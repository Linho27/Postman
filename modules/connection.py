#API connection module

# Libraries import
import requests

#Define API link
linkAPI = "http://127.0.0.1:5000"
#End points:
#   /everyPlate
#   /status/{pos}
#   /toggle/{pos}

#Function to get the position of a specific plate
def getPos(id):
    url = linkAPI + f'/everyPlate'
    try:
        # Get request to get info of every plate
        response = requests.get(url)
        
        # Verify if answer was successful
        if response.status_code == 200:
            plates = response.json()
            
            # Search plate by its id
            for position, data in plates.items():
                if data["numero_serie"] == id:
                    return position  # Return plate position
            return f"Peça com código de série {id} não encontrada."
        else:
            return f"Erro ao obter dados do servidor. Código de status: {response.status_code}"
    
    except requests.exceptions.RequestException as e:
        return f"Erro na requisição: {e}"

#Function to toggle position status
def togglePos(pos):
    #Check if position is within limits
    if not (1 <= pos <= 12):
        return "Número inválido. Deve estar entre 1 e 12."

    url = linkAPI + f"/toggle/{pos}"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            return f"Estado da peça {pos} alternado com sucesso."
        return f"Erro ao alternar o estado da peça {pos}. Código: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Erro na requisição: {e}"

#Function to check if a specific position is occupied    
def isOccupied(pos):
    url = linkAPI + f"/status/{pos}"    
    try:
        # Send GET request to the API
        response = requests.get(url)
        
        # Verify if answer was successful
        if response.status_code == 200:
            state = response.json()
            
            # Check if position is occupied
            return state.get(str(pos)) == "ocupado"
        else:
            print(f"Erro na requisição: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Erro na conexão com a API: {e}")
        return False