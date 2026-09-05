import math
import time
from typing import Any


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


def calcular_custo_paginas_lidas(paginas_lidas: int | float) -> int:
    """Normaliza o custo em páginas lidas para um número inteiro não negativo."""
    return max(0, int(paginas_lidas))


def buscar_chave_indice(indice_buckets: list[Bucket], chave: str) -> dict[str, Any]:
    """Busca uma chave no índice hash estático e informa custo e tempo."""
    inicio = time.perf_counter()

    if not indice_buckets:
        tempo_execucao = time.perf_counter() - inicio
        return {
            "chave": chave,
            "encontrada": False,
            "pagina": None,
            "bucket": None,
            "paginas_lidas": 0,
            "custo_paginas_lidas": 0,
            "tempo_execucao": tempo_execucao,
        }

    endereco_bucket = hash_customizado(chave, len(indice_buckets))
    bucket = indice_buckets[endereco_bucket]

    for pagina_id, registro_chave in ((registro[1], registro[0]) for registro in bucket.todos_registros()):
        if registro_chave == chave:
            tempo_execucao = time.perf_counter() - inicio
            return {
                "chave": chave,
                "encontrada": True,
                "pagina": pagina_id,
                "bucket": endereco_bucket,
                "paginas_lidas": 1,
                "custo_paginas_lidas": 1,
                "tempo_execucao": tempo_execucao,
            }

    tempo_execucao = time.perf_counter() - inicio
    return {
        "chave": chave,
        "encontrada": False,
        "pagina": None,
        "bucket": endereco_bucket,
        "paginas_lidas": 0,
        "custo_paginas_lidas": 0,
        "tempo_execucao": tempo_execucao,
    }


buscar_chave_por_indice_hash = buscar_chave_indice
buscar_chave_hash = buscar_chave_indice


def buscar_por_table_scan(paginas: list[list[str]], chave: str) -> dict[str, Any]:
    """Percorre página por página até encontrar a chave, contabilizando o custo."""
    inicio = time.perf_counter()
    paginas_lidas = 0

    for pagina_id, pagina in enumerate(paginas):
        paginas_lidas += 1
        if chave in pagina:
            tempo_execucao = time.perf_counter() - inicio
            return {
                "chave": chave,
                "encontrada": True,
                "pagina": pagina_id,
                "paginas_lidas": paginas_lidas,
                "custo_paginas_lidas": paginas_lidas,
                "tempo_execucao": tempo_execucao,
            }

    tempo_execucao = time.perf_counter() - inicio
    return {
        "chave": chave,
        "encontrada": False,
        "pagina": None,
        "paginas_lidas": paginas_lidas,
        "custo_paginas_lidas": paginas_lidas,
        "tempo_execucao": tempo_execucao,
    }


def comparar_buscas(resultado_indice: dict[str, Any], resultado_scan: dict[str, Any]) -> dict[str, float | int | bool | None]:
    """Compara tempo e custo entre busca indexada e table scan."""
    tempo_indice = float(resultado_indice.get("tempo_execucao", 0.0))
    tempo_scan = float(resultado_scan.get("tempo_execucao", 0.0))
    custo_indice = calcular_custo_paginas_lidas(resultado_indice.get("custo_paginas_lidas", 0))
    custo_scan = calcular_custo_paginas_lidas(resultado_scan.get("custo_paginas_lidas", 0))

    diferenca_tempo = tempo_scan - tempo_indice
    diferenca_custo = custo_scan - custo_indice
    ganho_tempo = (diferenca_tempo / tempo_scan * 100) if tempo_scan > 0 else 0.0
    ganho_custo = (diferenca_custo / custo_scan * 100) if custo_scan > 0 else 0.0

    return {
        "tempo_indice": tempo_indice,
        "tempo_scan": tempo_scan,
        "diferenca_tempo": diferenca_tempo,
        "ganho_tempo_percentual": ganho_tempo,
        "custo_indice": custo_indice,
        "custo_scan": custo_scan,
        "diferenca_custo": diferenca_custo,
        "ganho_custo_percentual": ganho_custo,
    }


table_scan = buscar_por_table_scan
