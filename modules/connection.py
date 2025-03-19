#API connection module

# Libraries import
import requests

def obter_pokemon(nome_ou_id):
    url = f"https://pokeapi.co/api/v2/pokemon/{nome_ou_id}"
    resposta = requests.get(url)
    
    if resposta.status_code == 200:
        return resposta.json()
    else:
        print("Erro ao obter dados do Pokémon.")
        return None

def getPos(id):
    url = f"<link da api>{id}"
    response = requests.get(url)    
    if response.status_code == 200:
        return response.json()
    else:
        print("Erro ao conectar.")
        return None