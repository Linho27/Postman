# ================================
# 🔗 API connection module
# ================================

# ================================
# 🔐 Environment Variables
# ================================
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("BASE_API")

# ================================
# 📦 Imports
# ================================
import requests

# ================================
# ⚙️ Functions
# ================================

# ================================
# 🔍 Return specific plate's position
# ================================
def getPos(id):
    url = API_BASE + f'/everyPlate'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            plates = response.json()
            for position, data in plates.items():
                if data["id"] == id:
                    return position
            return f"Peça com código de série {id} não encontrada."
        else:
            return f"Erro ao obter dados do servidor. Código de status: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Erro na requisição: {e}"

# ================================
# 🔄 Toggle position status
# ================================
def togglePos(pos):
    if not (1 <= pos <= 12):
        return "Número inválido. Deve estar entre 1 e 12."
    url = API_BASE + f"/toggle/{pos}"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            return f"Estado da peça {pos} alternado com sucesso."
        return f"Erro ao alternar o estado da peça {pos}. Código: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Erro na requisição: {e}"

# ================================
# ✅ Get position status
# ================================  
def isOccupied(pos):
    url = API_BASE + f"/status/{pos}"    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            state = response.json()
            pos_data = state.get(str(pos), {})
            return pos_data.get("estado") == "ocupado"
        else:
            print(f"Erro na requisição: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Erro na conexão com a API: {e}")
        return False