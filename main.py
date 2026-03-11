import random

# Exemplo de como deve ser a função
def girar_garrafa(participantes):
    if not participantes:
        return "Não há ninguém no grupo para participar!"
    
    # O random.choice seleciona um item aleatório da lista
    sorteado = random.choice(participantes)
    
    return f"A garrafa girou e parou em: {sorteado}!"

# Exemplo de lista de participantes
grupo = ["Alice", "Bruno", "Carlos", "Daniela", "Eduardo"]

# Chamando o comando
print(girar_garrafa(grupo))
