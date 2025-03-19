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

# Exemplo de utilização
pokemon = obter_pokemon("pikachu")
if pokemon:
    print(f"Nome: {pokemon['name']}")
    print(f"Altura: {pokemon['height']} cm")
    print(f"Peso: {pokemon['weight']} kg")
