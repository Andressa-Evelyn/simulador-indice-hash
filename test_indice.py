import importlib.util
import sys
import types
import unittest
from pathlib import Path


def carregar_modulo_indice():
    pacote_app = types.ModuleType("app")
    pacote_app.__path__ = [str(Path(__file__).parent / "app")]
    sys.modules["app"] = pacote_app

    especificacao = importlib.util.spec_from_file_location(
        "app.indice", Path(__file__).parent / "app" / "indice.py"
    )
    modulo = importlib.util.module_from_spec(especificacao)
    sys.modules["app.indice"] = modulo
    especificacao.loader.exec_module(modulo)
    return modulo


indice = carregar_modulo_indice()
Bucket = indice.Bucket
buscar_chave_indice = indice.buscar_chave_indice
buscar_por_table_scan = indice.buscar_por_table_scan
calcular_custo_paginas_lidas = indice.calcular_custo_paginas_lidas
comparar_buscas = indice.comparar_buscas
calcular_taxa_colisoes = indice.calcular_taxa_colisoes
calcular_taxa_overflow = indice.calcular_taxa_overflow
construir_indice = indice.construir_indice
quantidade_buckets_com_overflow = indice.quantidade_buckets_com_overflow
quantidade_colisoes = indice.quantidade_colisoes


class TestIndiceHash(unittest.TestCase):
    def test_bucket_na_capacidade_nao_tem_overflow(self):
        bucket = Bucket(3)
        registros = [(chave, 0) for chave in ("A", "B", "C")]

        for registro in registros:
            bucket.inserir(registro)

        self.assertEqual(bucket.registros, registros)
        self.assertFalse(bucket.possui_overflow)
        self.assertEqual(bucket.colisoes, 0)

    def test_quarto_registro_vai_para_overflow(self):
        bucket = Bucket(3)
        registros = [(str(indice), 0) for indice in range(4)]

        for registro in registros:
            bucket.inserir(registro)

        self.assertEqual(bucket.colisoes, 1)
        self.assertEqual(bucket.todos_registros(), registros)
        self.assertEqual(bucket.areas_overflow, [registros[3:]])

    def test_overflow_cria_mais_de_uma_area(self):
        bucket = Bucket(3)
        registros = [(str(indice), 0) for indice in range(7)]

        for registro in registros:
            bucket.inserir(registro)

        self.assertEqual([len(area) for area in bucket.areas_overflow], [3, 1])
        self.assertEqual(bucket.todos_registros(), registros)

    def test_estatisticas_sem_colisao(self):
        indice, _ = construir_indice([["a", "b", "c", "d"]], 3)

        self.assertEqual(quantidade_colisoes(indice), 0)
        self.assertEqual(calcular_taxa_colisoes(indice, 4), 0.0)
        self.assertEqual(calcular_taxa_overflow(indice), 0.0)

    def test_estatisticas_com_colisao_e_overflow(self):
        indice, _ = construir_indice([["a", "c", "e", "g"]], 3)

        self.assertEqual(quantidade_colisoes(indice), 1)
        self.assertEqual(calcular_taxa_colisoes(indice, 4), 25.0)
        self.assertEqual(quantidade_buckets_com_overflow(indice), 1)
        self.assertEqual(calcular_taxa_overflow(indice), 50.0)

    def test_indice_vazio(self):
        self.assertEqual(calcular_taxa_colisoes([], 0), 0.0)
        self.assertEqual(calcular_taxa_overflow([]), 0.0)

    def test_construcao_preserva_registros(self):
        paginas = [["a", "b"], ["c", "d"], ["e", "f"]]
        indice, _ = construir_indice(paginas, 2)

        total_no_indice = sum(len(bucket.todos_registros()) for bucket in indice)
        self.assertEqual(total_no_indice, sum(len(pagina) for pagina in paginas))

    def test_busca_por_indice_hash_e_table_scan(self):
        paginas = [["a", "b"], ["c", "d"], ["e", "f"]]
        indice_buckets, _ = construir_indice(paginas, 2)

        resultado_indice = buscar_chave_indice(indice_buckets, "d")
        self.assertTrue(resultado_indice["encontrada"])
        self.assertEqual(resultado_indice["pagina"], 1)
        self.assertEqual(resultado_indice["paginas_lidas"], 1)
        self.assertGreaterEqual(resultado_indice["tempo_execucao"], 0.0)
        self.assertEqual(calcular_custo_paginas_lidas(resultado_indice["paginas_lidas"]), 1)

        resultado_scan = buscar_por_table_scan(paginas, "d")
        self.assertTrue(resultado_scan["encontrada"])
        self.assertEqual(resultado_scan["pagina"], 1)
        self.assertEqual(resultado_scan["paginas_lidas"], 2)
        self.assertGreaterEqual(resultado_scan["tempo_execucao"], 0.0)

    def test_comparacao_tempo_e_custo(self):
        indice_resultado = {"tempo_execucao": 0.001, "custo_paginas_lidas": 1}
        scan_resultado = {"tempo_execucao": 0.010, "custo_paginas_lidas": 3}

        comparacao = comparar_buscas(indice_resultado, scan_resultado)

        self.assertAlmostEqual(comparacao["tempo_indice"], 0.001)
        self.assertAlmostEqual(comparacao["tempo_scan"], 0.010)
        self.assertGreater(comparacao["diferenca_tempo"], 0)
        self.assertEqual(comparacao["custo_indice"], 1)
        self.assertEqual(comparacao["custo_scan"], 3)
        self.assertEqual(comparacao["diferenca_custo"], 2)


if __name__ == "__main__":
    unittest.main()
