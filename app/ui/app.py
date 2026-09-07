import asyncio
from edifice import App, Button, HBoxView, Label, TextInput, VBoxView, VScrollView, Window, component, use_state

from app.data import carrega_arquivo, paginacao
from app.indice import buscar_chave_indice, buscar_por_table_scan, comparar_buscas, construir_indice
from app.ui.components import SelectFile, TotalInfo, Pages, Loading
from app.ui.styles import HEADER, SECTION_HEADER
from app.ui.hooks import use_debouce_state


def tamanho_pagina(value: str) -> int:
    if not value.strip():
        raise ValueError("Informe um tamanho de página maior que zero.")

    try:
        return int(value)
    except ValueError as error:
        raise ValueError("O tamanho da página deve ser um número inteiro.") from error


@component
def Screen(self):
    filepath, set_filepath = use_state("")
    total_words, set_total_words = use_state(0)
    pages, set_pages = use_state([])
    index_buckets, set_index_buckets = use_state([])
    search_key, set_search_key = use_state("")
    search_result, set_search_result = use_state(None)
    scan_result, set_scan_result = use_state(None)
    comparison, set_comparison = use_state({})
    message, set_message = use_state("Informe o tamanho da página e selecione um arquivo TXT.")
    is_message_error, set_is_message_error = use_state(False)
    is_loading, set_is_loading = use_state(False)

    async def update_page_size(value):
        if not filepath:
            return

        set_is_loading(True)
        set_is_message_error(False)
        await asyncio.sleep(0)

        try:
            page_size = tamanho_pagina(value)

            def _calcular():
                w = carrega_arquivo(filepath)
                p = paginacao(w, page_size)
                idx, _ = construir_indice(p, page_size)
                return w, p, idx

            words, created_pages, indice = await asyncio.to_thread(_calcular)
            set_total_words(len(words))
            set_pages(created_pages)
            set_index_buckets(indice)
            set_search_result(None)
            set_scan_result(None)
            set_comparison({})
            set_message("Paginação e índice atualizados.")
        except ValueError as error:
            set_pages([])
            set_index_buckets([])
            set_message(str(error))
            set_is_message_error(True)
        finally:
            set_is_loading(False)

    page_size_text, set_page_size_text = use_debouce_state("10", update_page_size)

    def select_file(file_path: str):
        try:
            set_is_message_error(False)
            page_size = tamanho_pagina(page_size_text)
            words = carrega_arquivo(file_path)
            created_pages = paginacao(words, page_size)
            indice, _ = construir_indice(created_pages, page_size)
        except ValueError as error:
            set_message(str(error))
            set_is_message_error(True)
            return

        set_filepath(file_path)
        set_total_words(len(words))
        set_pages(created_pages)
        set_index_buckets(indice)
        set_search_result(None)
        set_scan_result(None)
        set_comparison({})
        set_message("Dados carregados, páginas criadas e índice construído.")

    def executar_busca_indice(event):
        chave = search_key.strip()
        if not chave:
            set_message("Informe uma chave para realizar a busca por índice.")
            return
        if not pages:
            set_message("Carregue um arquivo antes de buscar.")
            return

        resultado = buscar_chave_indice(index_buckets, chave)
        set_search_result(resultado)
        if scan_result is not None:
            set_comparison(comparar_buscas(resultado, scan_result))
        set_message("Busca por índice executada.")

    def executar_table_scan(event):
        chave = search_key.strip()
        if not chave:
            set_message("Informe uma chave para realizar o table scan.")
            return
        if not pages:
            set_message("Carregue um arquivo antes do table scan.")
            return

        resultado = buscar_por_table_scan(pages, chave)
        set_scan_result(resultado)
        if search_result is not None:
            set_comparison(comparar_buscas(search_result, resultado))
        set_message("Table scan executado.")

    with VScrollView(style={'padding': 14, 'padding-top': 0, 'align': 'top'}):
        Label("Carga de dados e paginação", style=HEADER)

        SelectFile(filepath=filepath, on_file_change=select_file)

        with HBoxView():
            Label("Registros por página:")
            TextInput(
                text=page_size_text,
                placeholder_text="Ex.: 100",
                on_change=set_page_size_text,
            )

        Label(message, word_wrap=True, style={'padding': '14px 0', 'color': 'red' if is_message_error else None})

        TotalInfo(total_words=total_words, total_pages=len(pages))

        Pages(pages=pages, is_loading=is_loading)

        Label("Pesquisa por chave", style=SECTION_HEADER | { 'padding': '12px 0'})
        TextInput(
            text=search_key,
            placeholder_text="Digite a chave de busca",
            on_change=lambda value: set_search_key(value),
        )

        # if search_key.strip() and pages:
        with HBoxView(style={'padding-top': 12}):
            Button("Buscar por índice", on_click=executar_busca_indice)
            Button("Table Scan", on_click=executar_table_scan)

        if search_result is not None:
            estado = "encontrada" if search_result["encontrada"] else "não encontrada"
            Label(f"Busca por índice: {estado}")
            Label(f"Página: {search_result['pagina'] if search_result['pagina'] is not None else 'N/A'}")
            Label(f"Custo (páginas lidas): {search_result['custo_paginas_lidas']}")
            Label(f"Tempo de execução: {search_result['tempo_execucao']:.12f} s")

        if scan_result is not None:
            estado = "encontrada" if scan_result["encontrada"] else "não encontrada"
            Label(f"Table scan: {estado}")
            Label(f"Página: {scan_result['pagina'] if scan_result['pagina'] is not None else 'N/A'}")
            Label(f"Custo (páginas lidas): {scan_result['custo_paginas_lidas']}")
            Label(f"Tempo de execução: {scan_result['tempo_execucao']:.12f} s")

        if comparison:
            Label(
                "Comparação entre índice e table scan: "
                f"tempo índice={comparison['tempo_indice']:.12f}s, "
                f"tempo scan={comparison['tempo_scan']:.12f}s, "
                f"ganho={comparison['ganho_tempo_percentual']:.2f}%"
            )
            Label(
                "Custo: "
                f"índice={comparison['custo_indice']} páginas, "
                f"scan={comparison['custo_scan']} páginas, "
                f"diferença={comparison['diferenca_custo']} páginas"
            )


@component
def MainWindow(self):
    with Window(title="Simulador de Índice Hash Estático",
                icon="assets/hashtag.png",
                _size_open=(800, 600)):
        Screen()


def create_app():
    return App(MainWindow())

