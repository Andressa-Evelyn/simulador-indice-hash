import math
import time

class Bucket:
    def __init__(self, fr_capacidade: int):
        if fr_capacidade <= 0:
            raise ValueError("A capacidade do bucket deve ser maior que zero.")

        self.capacidade = fr_capacidade
        self.registros: list[tuple[str, int]] = []
        self.areas_overflow: list[list[tuple[str, int]]] = []
        self.colisoes = 0

    def inserir(self, registro: tuple[str, int]) -> None:
        if len(self.registros) < self.capacidade:
            self.registros.append(registro)
            return

        self.colisoes += 1
        if not self.areas_overflow or len(self.areas_overflow[-1]) >= self.capacidade:
            self.areas_overflow.append([])
        self.areas_overflow[-1].append(registro)

    def todos_registros(self) -> list[tuple[str, int]]:
        registros = self.registros.copy()
        for area in self.areas_overflow:
            registros.extend(area)
        return registros

    @property
    def possui_overflow(self) -> bool:
        return bool(self.areas_overflow)

def calcular_nb(nr: int, fr: int) -> int:
    if fr <= 0:
        raise ValueError("A capacidade do bucket deve ser maior que zero.")

    if nr == 0:
        return 1

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


def quantidade_colisoes(indice_buckets: list[Bucket]) -> int:
    return sum(bucket.colisoes for bucket in indice_buckets)


def quantidade_buckets_com_overflow(indice_buckets: list[Bucket]) -> int:
    return sum(bucket.possui_overflow for bucket in indice_buckets)


def calcular_taxa_colisoes(indice_buckets: list[Bucket], nr: int) -> float:
    if nr <= 0:
        return 0.0
    return quantidade_colisoes(indice_buckets) / nr * 100


def calcular_taxa_overflow(indice_buckets: list[Bucket]) -> float:
    if not indice_buckets:
        return 0.0
    return quantidade_buckets_com_overflow(indice_buckets) / len(indice_buckets) * 100

def construir_indice(paginas: list[list[str]], fr: int) -> tuple[list[Bucket], float]:
    tempo_inicio = time.time()
    
    nr = sum(len(pagina) for pagina in paginas)
    nb = calcular_nb(nr, fr)
    indice_buckets = [Bucket(fr) for _ in range(nb)]
    
    for id_pagina, pagina in enumerate(paginas):
        for chave in pagina:
            endereco_bucket = hash_customizado(chave, nb)
            indice_buckets[endereco_bucket].inserir((chave, id_pagina))
            
    tempo_fim = time.time()
    tempo_execucao = tempo_fim - tempo_inicio
    
    return indice_buckets, tempo_execucao