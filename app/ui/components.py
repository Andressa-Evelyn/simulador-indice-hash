import asyncio
import math
from typing import Callable
from os.path import basename
from edifice import component, HBoxView, VBoxView, Label, Button, Dropdown, TableGridView, TableGridRow, TabView, use_state, use_async, use_effect
from PySide6.QtWidgets import QFileDialog

from app.indice import (
    calcular_taxa_colisoes,
    calcular_taxa_overflow,
    quantidade_colisoes,
    quantidade_buckets_com_overflow,
)
from app.ui.styles import (
    get_theme_colors,
    get_primary_button_style,
    get_section_header_style,
)


@component
def InfoLabel(_, label: str, value: str):
    colors = get_theme_colors()
    with HBoxView(style={'align': 'left'}):
        Label(f'{label}: ', style={'font-weight': 'bold', 'font-size': 14, 'color': colors['text']})
        Label(value, style={'font-size': 14, 'color': colors['text']})


def use_timer(effect: Callable, interval=0.5):
    async def handle():
        while True:
            await asyncio.sleep(interval)
            effect()

    use_async(handle)


@component
def Loading(_, text: str = "Carregando", style={}):
    colors = get_theme_colors()
    dots, set_dots = use_state('.')

    def change_text():
        if len(dots) >= 3:
            set_dots('.')
        else:
            set_dots(dots + '.')

    use_timer(change_text, interval=0.3)

    Label(f'{text}{dots}', style={'color': colors['text_muted']} | style)


@component
def SelectFile(_, filepath: str,
               on_file_change: Callable[[str], None]):
    is_loading, set_is_loading = use_state(False)
    btn_style = get_primary_button_style()
    
    def select_file(_):
        set_is_loading(True)
        path, _ = QFileDialog.getOpenFileName(
            None,
            "Selecionar arquivo",
            "",
            "Arquivos de texto (*.txt);;Todos os arquivos (*)",
        )

        if not path:
            set_is_loading(False)
            return

        on_file_change(path)
        set_is_loading(False)

    with HBoxView(style={'padding-bottom': 12}):
        message = 'Arquivo' if not is_loading else 'Carregando arquivo'
        InfoLabel(message, basename(filepath) if filepath else 'nenhum selecionado')
        Button("Selecione o arquivo", on_click=select_file, style=btn_style | { 'max-width': '120px', 'opacity': 0.8 if is_loading else 1.0})


def format_time(seconds: float) -> str:
    if seconds is None:
        return "N/A"
    if seconds < 0.001:
        return f"{seconds * 1000:.4f} ms ({seconds:.8f} s)"
    if seconds < 1.0:
        return f"{seconds * 1000:.2f} ms ({seconds:.6f} s)"

    return f"{seconds:.4f} s"


def format_time_short(seconds: float) -> str:
    if seconds is None:
        return "N/A"
    if seconds < 0.001:
        return f"{seconds * 1000:.4f} ms"
    if seconds < 1.0:
        return f"{seconds * 1000:.2f} ms"

    return f"{seconds:.4f} s"


@component
def MetricBadge(_, title: str, value: str, subtitle: str, highlight_color: str | None = None, bg_color: str | None = None, border_color: str | None = None):
    colors = get_theme_colors()
    highlight = highlight_color or colors['accent']
    border = border_color or colors['border']

    with VBoxView(style={
        'border': f"1px solid {border}",
        'border-radius': 8,
        'padding-top': 10,
        'padding-bottom': 10,
        'padding-left': 14,
        'padding-right': 14,
        'margin': 4,
        'align': 'top',
        # 'min-width': '120px',
    }):
        Label(title, style={'font-size': 11, 'color': colors['text'], 'font-weight': 'bold'})
        Label(value, style={'font-size': 17, 'font-weight': 'bold', 'color': highlight, 'padding-top': 2, 'padding-bottom': 2})
        Label(subtitle, word_wrap=True, style={'font-size': 11, 'color': colors['text']})


@component
def TotalInfo(_, total_words: int, total_pages: int):
    colors = get_theme_colors()
    with HBoxView(style={'padding-bottom': 12}):
        MetricBadge(
            title="TOTAL DE PALAVRAS",
            value=f"{total_words}",
            subtitle=f"{total_words} registros carregados",
            highlight_color=colors["accent"],
        )
        MetricBadge(
            title="TOTAL DE PÁGINAS",
            value=f"{total_pages}",
            subtitle=f"{total_pages} página(s) gerada(s)",
            highlight_color=colors["accent"],
        )


@component
def Pages(
    _,
    pages: list = [],
    total_words: int = 0,
    is_loading: bool = False,
    highlight_page: int | None = None,
):
    colors = get_theme_colors()
    page, set_page = use_state(1)

    with VBoxView(style={'align': 'top'}):
        if is_loading:
            Loading(text="Carregando páginas")
        elif not pages:
            Label("Sem páginas ainda", style={"color": colors["text"]})
        else:
            total_w = total_words if total_words > 0 else sum(len(p) for p in pages)
            total_p = len(pages)

            TotalInfo(total_words=total_w, total_pages=total_p)

            page_size = 10
            total_pages_count = max(1, math.ceil(total_p / page_size))

            def update_page_on_highlight():
                if highlight_page is not None and total_p > 0 and 0 <= highlight_page < total_p:
                    target_page = (highlight_page // page_size) + 1
                    set_page(target_page)

            use_effect(update_page_on_highlight, [highlight_page])

            safe_page = max(1, min(page, total_pages_count))

            start_idx = (safe_page - 1) * page_size
            end_idx = min(start_idx + page_size, total_p)
            page_items_list = [(i, pages[i]) for i in range(start_idx, end_idx)]
            page_options = [
                f"Página {p} de {total_pages_count} (Páginas #{ (p - 1) * page_size } a #{ min(p * page_size, total_p) - 1 } de {total_p})"
                for p in range(1, total_pages_count + 1)
            ]

            with HBoxView(style={"padding-top": 6, "padding-bottom": 6, "align": "left"}):
                Label("Página:", style={"font-weight": "bold", "font-size": 13, "color": colors["text"], "margin-right": 8})
                Dropdown(
                    selection=safe_page - 1,
                    options=page_options,
                    on_select=lambda idx: set_page(idx + 1),
                )

            with VBoxView(style={"border": f"1px solid {colors['border_subtle']}", "border-radius": 6, "margin-top": 6}):
                with TableGridView(style={"padding": 4}):
                    with TableGridRow():
                        Label("Página", style={"font-weight": "bold", "background-color": colors["bg_subtle"], "padding": 8, "font-size": 13, "color": colors["text"]})
                        Label("Qtd. Registros", style={"font-weight": "bold", "background-color": colors["bg_subtle"], "padding": 8, "font-size": 13, "color": colors["text"]})
                        Label("Conteúdo da Página", style={"font-weight": "bold", "background-color": colors["bg_subtle"], "padding": 8, "font-size": 13, "color": colors["text"]})

                    for idx_loop, (page_idx, page_items) in enumerate(page_items_list):
                        is_highlighted = (highlight_page is not None and page_idx == highlight_page)
                        row_bg = colors["accent_subtle"] if is_highlighted else (colors["table_row_even"] if idx_loop % 2 == 0 else colors["table_row_odd"])
                        items_str = ", ".join(f"'{item}'" for item in page_items) if page_items else "Página vazia"
                        page_label = f"⭐ Página #{page_idx} (Acessada)" if is_highlighted else f"Página #{page_idx}"

                        with TableGridRow():
                            Label(page_label, style={"background-color": row_bg, "padding": 8, "font-size": 13, "font-weight": "bold" if is_highlighted else "600", "color": colors["accent"] if is_highlighted else colors["text"]})
                            Label(f"{len(page_items)} registro(s)", style={"background-color": row_bg, "padding": 8, "font-size": 13, "font-weight": "bold" if is_highlighted else "normal", "color": colors["accent"] if is_highlighted else colors["text"]})
                            Label(items_str, word_wrap=True, style={"background-color": row_bg, "padding": 8, "font-size": 13, "font-weight": "bold" if is_highlighted else "normal", "color": colors["text"]})


@component
def Buckets(
    _,
    buckets: list = [],
    total_words: int = 0,
    build_time: float = 0.0,
    is_loading: bool = False,
    highlight_bucket: int | None = None,
):
    colors = get_theme_colors()
    page, set_page = use_state(1)

    with VBoxView():
        if is_loading:
            Loading(text="Carregando buckets")
        elif not buckets:
            Label("Sem buckets ainda", style={"color": colors["text"]})
        else:
            nb = len(buckets)
            fr = buckets[0].capacidade if buckets else 0
            total_colisoes = quantidade_colisoes(buckets)
            taxa_colisoes = calcular_taxa_colisoes(buckets, total_words)
            qtd_overflow = quantidade_buckets_com_overflow(buckets)
            taxa_overflow = calcular_taxa_overflow(buckets)

            page_size = 5
            total_pages = max(1, math.ceil(nb / page_size))

            def update_bucket_page_on_highlight():
                if highlight_bucket is not None and nb > 0 and 0 <= highlight_bucket < nb:
                    target_page = (highlight_bucket // page_size) + 1
                    set_page(target_page)

            use_effect(update_bucket_page_on_highlight, [highlight_bucket])

            safe_page = max(1, min(page, total_pages))

            start_idx = (safe_page - 1) * page_size
            end_idx = min(start_idx + page_size, nb)
            page_buckets = [(i, buckets[i]) for i in range(start_idx, end_idx)]
            page_options = [
                f"Página {p} de {total_pages} (Buckets #{ (p - 1) * page_size } a #{ min(p * page_size, nb) - 1 } de {nb})"
                for p in range(1, total_pages + 1)
            ]

            with HBoxView(style={"padding-bottom": 8}):
                MetricBadge(
                    title="TOTAL DE BUCKETS",
                    value=f"NB: {nb}",
                    subtitle=f"{total_words} registros no total",
                    highlight_color=colors["accent"],
                )
                MetricBadge(
                    title="CAPACIDADE DO BUCKET",
                    value=f"FR: {fr} chaves",
                    subtitle="Cap. máxima suportada",
                    highlight_color=colors["accent"],
                )
                MetricBadge(
                    title="TEMPO DE CONSTRUÇÃO",
                    value=format_time_short(build_time),
                    subtitle=format_time(build_time),
                    highlight_color=colors["accent"],
                )

                MetricBadge(
                    title="TAXA DE COLISÕES",
                    value=f"{taxa_colisoes:.2f}%",
                    subtitle=f"{total_colisoes} colisão(ões) no total",
                    highlight_color=colors["danger"] if total_colisoes > 0 else colors["success"],
                    bg_color=colors["danger_bg"] if total_colisoes > 0 else colors["success_bg"],
                    border_color=colors["danger_border"] if total_colisoes > 0 else colors["success_border"],
                )
                MetricBadge(
                    title="BUCKETS EM OVERFLOW",
                    value=f"{qtd_overflow} bucket(s)",
                    subtitle=f"{qtd_overflow} de {nb} em overflow",
                    highlight_color=colors["danger"] if qtd_overflow > 0 else colors["success"],
                    bg_color=colors["danger_bg"] if qtd_overflow > 0 else colors["success_bg"],
                    border_color=colors["danger_border"] if qtd_overflow > 0 else colors["success_border"],
                )
                MetricBadge(
                    title="TAXA DE OVERFLOW",
                    value=f"{taxa_overflow:.2f}%",
                    subtitle=f"{qtd_overflow}/{nb} buckets com overflow",
                    highlight_color=colors["danger"] if taxa_overflow > 0 else colors["success"],
                    bg_color=colors["danger_bg"] if taxa_overflow > 0 else colors["success_bg"],
                    border_color=colors["danger_border"] if taxa_overflow > 0 else colors["success_border"],
                )

            with HBoxView(style={"padding-top": 6, "padding-bottom": 6, "align": "left"}):
                Label("Página:", style={"font-weight": "bold", "font-size": 13, "color": colors["text"], "margin-right": 8})
                Dropdown(
                    selection=safe_page - 1,
                    options=page_options,
                    on_select=lambda idx: set_page(idx + 1),
                )

            with VBoxView(style={"border": f"1px solid {colors['border_subtle']}", "border-radius": 6, "margin-top": 6}):
                with TableGridView(style={"padding": 4}):
                    with TableGridRow():
                        Label("Bucket", style={"font-weight": "bold", "background-color": colors["bg_subtle"], "padding": 8, "font-size": 13, "color": colors["text"]})
                        Label("Ocupação", style={"font-weight": "bold", "background-color": colors["bg_subtle"], "padding": 8, "font-size": 13, "color": colors["text"]})
                        Label("Colisões", style={"font-weight": "bold", "background-color": colors["bg_subtle"], "padding": 8, "font-size": 13, "color": colors["text"]})
                        Label("Overflow", style={"font-weight": "bold", "background-color": colors["bg_subtle"], "padding": 8, "font-size": 13, "color": colors["text"]})
                        Label("Registros Principais (Chave → Pág)", style={"font-weight": "bold", "background-color": colors["bg_subtle"], "padding": 8, "font-size": 13, "color": colors["text"]})
                        Label("Registros em Overflow (Chave → Pág)", style={"font-weight": "bold", "background-color": colors["bg_subtle"], "padding": 8, "font-size": 13, "color": colors["text"]})

                    for idx_loop, (bucket_idx, bucket) in enumerate(page_buckets):
                        is_highlighted = (highlight_bucket is not None and bucket_idx == highlight_bucket)
                        row_bg = colors["accent_subtle"] if is_highlighted else (colors["table_row_even"] if idx_loop % 2 == 0 else colors["table_row_odd"])
                        bucket_label = f"⭐ Bucket #{bucket_idx} (Acessado)" if is_highlighted else f"Bucket #{bucket_idx}"
                        reg_str = ", ".join(f"'{chave}' (pág. {pag})" for chave, pag in bucket.registros) if bucket.registros else "Vazio"
                        if bucket.possui_overflow:
                            over_str = ", ".join(f"'{chave}' (pág. {pag})" for area in bucket.areas_overflow for chave, pag in area)
                            total_over = sum(len(a) for a in bucket.areas_overflow)
                            overflow_display = f"Sim ({total_over})"
                        else:
                            over_str = "—"
                            overflow_display = "Não"

                        with TableGridRow():
                            Label(bucket_label, style={"background-color": row_bg, "padding": 8, "font-size": 13, "font-weight": "bold" if is_highlighted else "600", "color": colors["accent"] if is_highlighted else colors["text"]})
                            Label(f"{len(bucket.registros)}/{bucket.capacidade}", style={"background-color": row_bg, "padding": 8, "font-size": 13, "color": colors["text"]})
                            Label(f"{bucket.colisoes}", style={"background-color": row_bg, "padding": 8, "font-size": 13, "color": colors["danger"] if bucket.colisoes > 0 else colors["text"]})
                            Label(overflow_display, style={"background-color": row_bg, "padding": 8, "font-size": 13, "font-weight": "600", "color": colors["danger"] if bucket.possui_overflow else colors["success"]})
                            Label(reg_str, word_wrap=True, style={"background-color": row_bg, "padding": 8, "font-size": 13, "color": colors["text"]})
                            Label(over_str, word_wrap=True, style={"background-color": row_bg, "padding": 8, "font-size": 13, "color": colors["danger"] if bucket.possui_overflow else colors["text_muted"]})


@component
def DataInfo(
    _,
    total_words: int,
    pages: list,
    buckets: list = [],
    build_time: float = 0.0,
    is_loading: bool = False,
    highlight_page: int | None = None,
    highlight_bucket: int | None = None,
):
    with VBoxView():
        Label("Informações", style=get_section_header_style())

        with TabView(labels=['Páginas', 'Buckets']):
            Pages(
                pages=pages,
                total_words=total_words,
                is_loading=is_loading,
                highlight_page=highlight_page,
            ).set_key('Páginas')
            Buckets(
                buckets=buckets,
                total_words=total_words,
                build_time=build_time,
                is_loading=is_loading,
                highlight_bucket=highlight_bucket,
            ).set_key('Buckets')


@component
def SearchResultCard(
    _,
    title: str,
    result: dict | None,
    is_index: bool = False,
    placeholder_text: str = "Nenhuma busca realizada.",
):
    colors = get_theme_colors()
    with VBoxView(style={
        'background-color': colors['card_bg'],
        'border': f"1px solid {colors['border']}",
        'border-radius': 8,
        'padding': 12,
        'margin': 4,
        'align': 'top',
        'min-width': '330px',
    }):
        with HBoxView(style={'align': 'left', 'padding-bottom': 8}):
            Label(title, style={'font-weight': 'bold', 'font-size': 15, 'color': colors['text']})
            if result is not None:
                result_found = result.get("encontrada", False)
                with HBoxView(style={'align': 'right'}):
                    Label(
                        "✅ Encontrada" if result_found else "❌ Não encontrada",
                        style={
                            'color': colors['success'] if result_found else colors['danger'],
                            'padding-top': 2,
                            'padding-bottom': 2,
                            'padding-left': 8,
                            'padding-right': 8,
                            'font-weight': 'bold',
                            'font-size': 11,
                        }
                    )

        if result is None:
            with VBoxView(style={'padding-top': 16, 'padding-bottom': 16, 'padding-left': 0, 'padding-right': 0, 'align': 'center'}):
                Label(placeholder_text, style={'color': colors['text_muted'], 'font-style': 'italic', 'font-size': 13})
        else:
            pagina = result.get("pagina")
            pagina_str = f"Página {pagina}" if pagina is not None else "N/A"
            custo = result.get("custo_paginas_lidas", 0)
            tempo = result.get("tempo_execucao", 0.0)
            bucket = result.get("bucket")

            with TableGridView(style={'padding-top': 8}):
                with TableGridRow():
                    Label("Chave buscada:", style={'font-weight': 'bold', 'padding-top': 4, 'padding-bottom': 4, 'padding-right': 8, 'padding-left': 0, 'font-size': 13, 'color': colors['text_muted']})
                    Label(f'"{result.get("chave", "")}"', style={'padding-top': 4, 'padding-bottom': 4, 'padding-left': 0, 'padding-right': 0, 'font-size': 13, 'font-weight': '600', 'color': colors['text']})

                if is_index and bucket is not None:
                    with TableGridRow():
                        Label("Bucket Hash (acessado):", style={'font-weight': 'bold', 'padding-top': 4, 'padding-bottom': 4, 'padding-right': 8, 'padding-left': 0, 'font-size': 13, 'color': colors['text_muted']})
                        Label(f"Bucket #{bucket}", style={'padding-top': 4, 'padding-bottom': 4, 'padding-left': 0, 'padding-right': 0, 'font-size': 13, 'font-weight': 'bold', 'color': colors['accent']})

                with TableGridRow():
                    label_loc = "Página acessada:" if is_index else "Localização:"
                    loc_val = f"Página #{pagina}" if pagina is not None else "N/A"
                    Label(label_loc, style={'font-weight': 'bold', 'padding-top': 4, 'padding-bottom': 4, 'padding-right': 8, 'padding-left': 0, 'font-size': 13, 'color': colors['text_muted']})
                    Label(
                        loc_val,
                        style={
                            'padding-top': 4,
                            'padding-bottom': 4,
                            'padding-left': 0,
                            'padding-right': 0,
                            'font-size': 13,
                            'font-weight': 'bold' if (is_index and pagina is not None) else '600',
                            'color': colors['accent'] if (is_index and pagina is not None) else colors['text'],
                        }
                    )

                with TableGridRow():
                    Label("Custo (I/O páginas):", style={'font-weight': 'bold', 'padding-top': 4, 'padding-bottom': 4, 'padding-right': 8, 'padding-left': 0, 'font-size': 13, 'color': colors['text_muted']})
                    Label(f"{custo} página(s) lida(s)", style={'padding-top': 4, 'padding-bottom': 4, 'padding-left': 0, 'padding-right': 0, 'font-size': 13, 'font-weight': '600', 'color': colors['accent'] if is_index else colors['danger']})

                with TableGridRow():
                    Label("Tempo de execução:", style={'font-weight': 'bold', 'padding-top': 4, 'padding-bottom': 4, 'padding-right': 8, 'padding-left': 0, 'font-size': 13, 'color': colors['text_muted']})
                    Label(format_time(tempo), style={'padding-top': 4, 'padding-bottom': 4, 'padding-left': 0, 'padding-right': 0, 'font-size': 13, 'color': colors['text']})


def conclusion_text(diff, custo_ind, custo_scn, ganho_custo, bucket=None):
    bucket_info = f" (mapeada no Bucket #{bucket})" if bucket is not None else ""
    if diff > 0:
        return (
            f"💡 Conclusão: A busca por Índice Hash acessou diretamente a página alvo{bucket_info} (custo de {custo_ind} página), "
            f"enquanto o Table Scan precisou percorrer sequencialmente {custo_scn} páginas. "
            f"Isso gerou uma economia de {diff} leituras de página ({ganho_custo:.1f}% menor custo de I/O)."
        )
    if custo_ind == custo_scn:
        return f"💡 Conclusão: O registro estava na primeira página{bucket_info}, logo ambos os métodos realizaram a leitura de 1 página."

    return "💡 Conclusão: Comparação realizada entre os dois métodos de busca."


@component
def ComparisonDashboard(_, search_result: dict, scan_result: dict, comparison: dict):
    colors = get_theme_colors()
    custo_ind = comparison.get("custo_indice", 0)
    custo_scn = comparison.get("custo_scan", 0)
    dif_custo = comparison.get("diferenca_custo", 0)
    ganho_custo = comparison.get("ganho_custo_percentual", 0.0)

    tempo_ind = comparison.get("tempo_indice", 0.0)
    tempo_scn = comparison.get("tempo_scan", 0.0)
    dif_tempo = comparison.get("diferenca_tempo", 0.0)
    ganho_tempo = comparison.get("ganho_tempo_percentual", 0.0)

    speedup_text = ""
    if tempo_ind > 0 and tempo_scn > 0:
        factor = tempo_scn / tempo_ind
        if factor >= 1.0:
            speedup_text = f" ({factor:.1f}x mais rápido)"

    with VBoxView(style={
        'background-color': colors['card_bg'],
        'border': f"1px solid {colors['border']}",
        'border-radius': 8,
        'padding': 18,
        'margin-top': 12,
        'margin-bottom': 12,
    }):
        Label("⚖️ Comparativo de Desempenho (Índice vs. Table Scan)", style={'font-weight': 'bold', 'font-size': 16, 'padding-bottom': 10, 'color': colors['text']})

        with HBoxView(style={'padding-bottom': 12}):
            MetricBadge(
                title="ECONOMIA DE I/O (PÁGINAS)",
                value=f"{dif_custo} pág(s) economizada(s)",
                subtitle=f"Redução de {ganho_custo:.1f}% em acessos a disco",
                highlight_color=colors['success'] if dif_custo > 0 else colors['text_muted'],
                bg_color=colors['success_bg'] if dif_custo > 0 else colors['bg_subtle'],
                border_color=colors['success_border'] if dif_custo > 0 else colors['border'],
            )
            MetricBadge(
                title="GANHO DE TEMPO",
                value=f"{ganho_tempo:+.1f}%{speedup_text}",
                subtitle=f"Diferença de {format_time_short(abs(dif_tempo))} ({format_time_short(tempo_ind)} vs {format_time_short(tempo_scn)})",
                highlight_color=colors['success'] if ganho_tempo > 0 else colors['danger'] if ganho_tempo < 0 else colors['text_muted'],
                bg_color=colors['success_bg'] if ganho_tempo > 0 else colors['danger_bg'] if ganho_tempo < 0 else colors['bg_subtle'],
                border_color=colors['success_border'] if ganho_tempo > 0 else colors['danger_border'] if ganho_tempo < 0 else colors['border'],
            )

        with VBoxView(style={'border': f"1px solid {colors['border_subtle']}", 'border-radius': 6}):
            with TableGridView(style={'padding': 4}):
                with TableGridRow():
                    Label("Métrica", style={'font-weight': 'bold', 'background-color': colors['bg_subtle'], 'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'color': colors['text']})
                    Label("Busca por Índice Hash", style={'font-weight': 'bold', 'background-color': colors['bg_subtle'], 'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'color': colors['accent']})
                    Label("Table Scan", style={'font-weight': 'bold', 'background-color': colors['bg_subtle'], 'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'color': colors['danger']})
                    Label("Diferença / Vantagem", style={'font-weight': 'bold', 'background-color': colors['bg_subtle'], 'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'color': colors['success']})

                with TableGridRow():
                    Label("Status", style={'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'color': colors['text']})
                    Label("Encontrada" if search_result.get("encontrada") else "Não encontrada", style={'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'color': colors['text']})
                    Label("Encontrada" if scan_result.get("encontrada") else "Não encontrada", style={'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'color': colors['text']})
                    Label("Idêntico" if search_result.get("encontrada") == scan_result.get("encontrada") else "Divergente", style={'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'font-weight': '600', 'color': colors['text']})

                bucket_ind = search_result.get("bucket")
                with TableGridRow():
                    Label("Bucket Hash", style={'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'background-color': colors['bg_alt'], 'color': colors['text']})
                    Label(f"Bucket #{bucket_ind}" if bucket_ind is not None else "N/A", style={'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'background-color': colors['bg_alt'], 'font-weight': 'bold' if bucket_ind is not None else 'normal', 'color': colors['accent'] if bucket_ind is not None else colors['text']})
                    Label("N/A", style={'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'background-color': colors['bg_alt'], 'color': colors['text_muted']})
                    Label(f"Mapeado no Bucket #{bucket_ind}" if bucket_ind is not None else "—", style={'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'background-color': colors['bg_alt'], 'color': colors['text']})

                pag_ind = search_result.get("pagina")
                pag_scn = scan_result.get("pagina")
                with TableGridRow():
                    Label("Página", style={'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'color': colors['text']})
                    Label(f"Página #{pag_ind}" if pag_ind is not None else "N/A", style={'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'color': colors['accent'] if pag_ind is not None else colors['text'], 'font-weight': 'bold' if pag_ind is not None else 'normal'})
                    Label(f"Página #{pag_scn}" if pag_scn is not None else "N/A", style={'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'color': colors['text']})
                    Label("Mesma página" if pag_ind == pag_scn else "Diferente", style={'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'color': colors['success'] if pag_ind == pag_scn else colors['danger']})

                with TableGridRow():
                    Label("Páginas Lidas (I/O)", style={'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'background-color': colors['bg_alt'], 'font-weight': '600', 'color': colors['text']})
                    Label(f"{custo_ind} página(s)", style={'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'background-color': colors['bg_alt'], 'color': colors['accent'], 'font-weight': '600'})
                    Label(f"{custo_scn} página(s)", style={'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'background-color': colors['bg_alt'], 'color': colors['danger'], 'font-weight': '600'})
                    Label(f"-{dif_custo} páginas ({ganho_custo:.1f}%)" if dif_custo > 0 else f"{dif_custo} páginas", style={'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'background-color': colors['bg_alt'], 'font-weight': 'bold', 'color': colors['success'] if dif_custo > 0 else colors['text_muted']})

                with TableGridRow():
                    Label("Tempo de Execução", style={'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'color': colors['text']})
                    Label(format_time_short(tempo_ind), style={'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'color': colors['text']})
                    Label(format_time_short(tempo_scn), style={'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'color': colors['text']})
                    Label(f"{ganho_tempo:+.1f}%" if ganho_tempo != 0 else "0.0%", style={'padding-top': 8, 'padding-bottom': 8, 'padding-left': 10, 'padding-right': 10, 'font-size': 13, 'font-weight': 'bold', 'color': colors['success'] if ganho_tempo > 0 else colors['danger'] if ganho_tempo < 0 else colors['text_muted']})

        with VBoxView(style={'padding-top': 10}):
            conclusao = conclusion_text(dif_custo, custo_ind, custo_scn, ganho_custo, search_result.get("bucket"))
            Label(conclusao, word_wrap=True, style={'color': colors['text'], 'font-size': 12, 'background-color': colors['bg_subtle'], 'padding-top': 8, 'padding-bottom': 8, 'padding-left': 12, 'padding-right': 12, 'border-radius': 6})
