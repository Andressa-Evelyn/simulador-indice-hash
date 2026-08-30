import math
import time

class Bucket:
    def __init__(self, fr_capacidade: int):
        self.capacidade = fr_capacidade
        self.registros: list[tuple[str, int]] = []

def calcular_nb(nr: int, fr: int) -> int:
    nb = math.ceil(nr / fr)
    if nb <= (nr / fr):
        nb += 1
    return nb

def hash_customizado(chave: str, nb: int) -> int:
    valor_hash = 0
    primo = 31
    for i, caractere in enumerate(chave):
        valor_hash += ord(caractere) * (primo ** i)
    return valor_hash % nb

def construir_indice(paginas: list[list[str]], fr: int) -> tuple[list[Bucket], float]:
    tempo_inicio = time.time()
    
    nr = sum(len(pagina) for pagina in paginas)
    nb = calcular_nb(nr, fr)
    indice_buckets = [Bucket(fr) for _ in range(nb)]
    
    for id_pagina, pagina in enumerate(paginas):
        for chave in pagina:
            endereco_bucket = hash_customizado(chave, nb)
            # A equipe (HU07/HU08) precisará adicionar a checagem de Overflow aqui depois
            indice_buckets[endereco_bucket].registros.append((chave, id_pagina))
            
    tempo_fim = time.time()
    tempo_execucao = tempo_fim - tempo_inicio
    
    return indice_buckets, tempo_execucao