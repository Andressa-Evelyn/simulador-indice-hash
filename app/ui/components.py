import asyncio
from typing import Callable
from os.path import basename
from edifice import component, HBoxView, VBoxView, Label, Button, TableGridView, TableGridRow, use_state, use_async
from PySide6.QtWidgets import QFileDialog

from app.ui.styles import PRIMARY_BUTTON, SECTION_HEADER


@component
def InfoLabel(_, label: str, value: str):
    with HBoxView(style={'align': 'left'}):
        Label(f'{label}: ', style={'font-weight': 'bold', 'font-size': 14})
        Label(value, style={'font-size': 14})


def use_timer(effect: Callable, interval=0.5):
    async def handle():
        while True:
            await asyncio.sleep(interval)
            effect()

    use_async(handle)


@component
def Loading(_, text: str = "Carregando", style={}):
    dots, set_dots = use_state('.')

    def change_text():
        if len(dots) >= 3:
            set_dots('.')
        else:
            set_dots(dots + '.')

    use_timer(change_text, interval=0.3)

    Label(f'{text}{dots}', style=style)

    


@component
def SelectFile(_, filepath: str,
               on_file_change: Callable[[str], None]):
    is_loading, set_is_loading = use_state(False)
    
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
        Button("Selecione o arquivo", on_click=select_file, style=PRIMARY_BUTTON | { 'max-width': '120px', 'opacity': 0.8 if is_loading else 1.0})


@component
def TotalInfo(_, total_words: int, total_pages: int):
    with HBoxView(style={'padding-bottom': 12}):
        InfoLabel("Total de palavras", str(total_words))
        InfoLabel("Total de páginas", str(total_pages))


@component
def TablePagePreview(_, page_number: int, items = [], style={}):
    last_index = len(items) - 1
    with VBoxView(style=style | {'padding': 6}):
        with VBoxView(style={'align': 'top', 'border-radius': 7}):
            Label(f'Página {page_number}', style={
                'font-weight': 'bold',
                'padding': 6
            })
            with TableGridView():
                if not items:
                    Label('Página sem conteúdo')

                for index, record in enumerate(items):
                    is_last_item = index == last_index
                    with TableGridRow():
                        Label(record, style= style | {
                            'background-color': '#efefef' if index % 2 else "#8f8f8f",
                            'color': '#010101',
                            'padding': 6,
                            'border-bottom-right-radius': 6 if is_last_item else 0,
                            'border-bottom-left-radius': 6 if is_last_item else 0
                            })


@component
def Pages(_, pages=[], is_loading: bool = False):
    with VBoxView():
        Label("Páginas", style=SECTION_HEADER)
        if is_loading:
            Loading(text="Carregando páginas")
        elif pages:
            # Label(page_preview(1, pages[0]), word_wrap=True)
            with HBoxView(style={'padding-bottom': 12}):
                TablePagePreview(1, pages[0][:5])

                TablePagePreview(
                    len(pages) if len(pages) > 1 else 'última página',
                    pages[-1][-5:] if len(pages) > 1 else []
                )
            # if len(pages) > 1:
            #     Label(page_preview(len(pages), pages[-1]), word_wrap=True)
        else:
            Label('Sem páginas ainda')
