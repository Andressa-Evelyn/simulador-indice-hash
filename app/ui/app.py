import asyncio
from edifice import App, Button, HBoxView, Label, TextInput, VBoxView, VScrollView, TabView, Window, component, use_palette_edifice, use_state

from app.data import carrega_arquivo, paginacao
from app.indice import buscar_chave_indice, buscar_por_table_scan, comparar_buscas, construir_indice
from app.ui.components import SelectFile, DataInfo, SearchResultCard, ComparisonDashboard
from app.ui.styles import (
    get_theme_colors,
    get_header_style,
    get_section_header_style,
    get_primary_button_style,
    get_secondary_button_style,
)
from app.ui.hooks import use_debouce_state


def tamanho_pagina(value: str) -> int:
    if not value.strip():
        raise ValueError("Informe um tamanho de página maior que zero.")

    try:
        return int(value)
    except ValueError as error:
        raise ValueError("O tamanho da página deve ser um número inteiro.") from error


@component
def Screen(_):
    colors = get_theme_colors()
    filepath, set_filepath = use_state("")
    total_words, set_total_words = use_state(0)
    pages, set_pages = use_state([])
    index_buckets, set_index_buckets = use_state([])
    build_time, set_build_time = use_state(0.0)
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
                idx, t_idx = construir_indice(p, page_size)
                return w, p, idx, t_idx

            words, created_pages, indice, t_idx = await asyncio.to_thread(_calcular)
            set_total_words(len(words))
            set_pages(created_pages)
            set_index_buckets(indice)
            set_build_time(t_idx)
            set_search_result(None)
            set_scan_result(None)
            set_comparison({})
            set_message("Paginação e índice atualizados.")
        except ValueError as error:
            set_pages([])
            set_index_buckets([])
            set_build_time(0.0)
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
            indice, t_idx = construir_indice(created_pages, page_size)
        except ValueError as error:
            set_message(str(error))
            set_is_message_error(True)
            return

        set_filepath(file_path)
        set_total_words(len(words))
        set_pages(created_pages)
        set_index_buckets(indice)
        set_build_time(t_idx)
        set_search_result(None)
        set_scan_result(None)
        set_comparison({})
        set_message("Dados carregados, páginas criadas e índice construído.")

    def executar_busca_indice(_):
        chave = search_key.strip()
        if not chave:
            set_message("Informe uma chave para realizar a busca por índice.")
            return
        if not pages:
            set_message("Carregue um arquivo antes de buscar.")
            return

        resultado = buscar_chave_indice(index_buckets, chave)
        set_search_result(resultado)
        if scan_result is not None and scan_result.get("chave") == chave:
            set_comparison(comparar_buscas(resultado, scan_result))
        else:
            set_comparison({})
        set_message("Busca por índice executada.")

    def executar_table_scan(_):
        chave = search_key.strip()
        if not chave:
            set_message("Informe uma chave para realizar o table scan.")
            return
        if not pages:
            set_message("Carregue um arquivo antes do table scan.")
            return

        resultado = buscar_por_table_scan(pages, chave)
        set_scan_result(resultado)
        if search_result is not None and search_result.get("chave") == chave:
            set_comparison(comparar_buscas(search_result, resultado))
        else:
            set_comparison({})
        set_message("Table scan executado.")

    def executar_ambas(_):
        chave = search_key.strip()
        if not chave:
            set_message("Informe uma chave para realizar a busca.")
            return
        if not pages:
            set_message("Carregue um arquivo antes de buscar.")
            return

        resultado_indice = buscar_chave_indice(index_buckets, chave)
        resultado_scan = buscar_por_table_scan(pages, chave)
        set_search_result(resultado_indice)
        set_scan_result(resultado_scan)
        set_comparison(comparar_buscas(resultado_indice, resultado_scan))
        set_message("Buscas por índice e Table Scan executadas e comparadas.")

    header_style = get_header_style()
    section_header_style = get_section_header_style()
    primary_btn_style = get_primary_button_style()
    secondary_btn_style = get_secondary_button_style()

    with VBoxView(style={'padding': 14, 'padding-top': 0, 'align': 'top'}):
        Label("Carga de dados e paginação", style=header_style)

        SelectFile(filepath=filepath, on_file_change=select_file)

        with HBoxView():
            Label("Registros por página:", style={'color': colors['text'], 'font-size': 13})
            TextInput(
                text=page_size_text,
                placeholder_text="Ex.: 100",
                on_change=set_page_size_text,
            )

        Label(message, word_wrap=True, style={'padding-top': 14, 'padding-bottom': 14, 'color': colors['danger'] if is_message_error else colors['text_muted']})

        DataInfo(
            total_words=total_words,
            pages=pages,
            buckets=index_buckets,
            build_time=build_time,
            is_loading=is_loading,
        )

        Label("Pesquisa por chave", style=section_header_style | {'padding-top': 12, 'padding-bottom': 6})
        TextInput(
            text=search_key,
            placeholder_text="Digite a chave de busca",
            on_change=lambda value: set_search_key(value),
        )

        with HBoxView(style={'padding-top': 10, 'padding-bottom': 12}):
            Button("Buscar por índice", on_click=executar_busca_indice, style=primary_btn_style | {'margin-right': 6})
            Button("Table Scan", on_click=executar_table_scan, style=secondary_btn_style | {'margin-right': 6})
            Button("Executar Ambas e Comparar", on_click=executar_ambas, style=secondary_btn_style)

        if search_result is not None or scan_result is not None:
            with HBoxView(style={'padding-top': 6, 'align': 'top'}):
                SearchResultCard(
                    title="🔍 Busca por Índice Hash",
                    result=search_result,
                    is_index=True,
                    placeholder_text="Execute a busca por índice para visualizar o resultado.",
                )
                SearchResultCard(
                    title="📋 Table Scan (Busca Sequencial)",
                    result=scan_result,
                    is_index=False,
                    placeholder_text="Execute o Table Scan para visualizar o resultado.",
                )

        if comparison and search_result is not None and scan_result is not None:
            ComparisonDashboard(
                search_result=search_result,
                scan_result=scan_result,
                comparison=comparison,
            )


@component
def MainWindow(_):
    use_palette_edifice()
    with Window(title="Simulador de Índice Hash Estático",
                icon="assets/hashtag.png",
                _size_open=(800, 600)):
        with VScrollView():
            Screen()


def create_app():
    return App(MainWindow())

