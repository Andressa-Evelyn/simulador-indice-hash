from edifice import App, Button, HBoxView, Label, TextInput, VBoxView, Window, component, use_state
from PySide6.QtWidgets import QFileDialog
from os.path import basename

from app.data import carrega_arquivo, paginacao


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
    page_size_text, set_page_size_text = use_state("10")
    total_words, set_total_words = use_state(0)
    pages, set_pages = use_state([])
    message, set_message = use_state("Informe o tamanho da página e selecione um arquivo TXT.")

    def select_file(event):
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Selecionar arquivo",
            "",
            "Arquivos de texto (*.txt);;Todos os arquivos (*)",
        )

        if not file_path:
            return

        try:
            page_size = tamanho_pagina(page_size_text)
            words = carrega_arquivo(file_path)
            created_pages = paginacao(words, page_size)
        except ValueError as error:
            set_message(str(error))
            return

        set_filepath(file_path)
        set_total_words(len(words))
        set_pages(created_pages)
        set_message("Dados carregados e divididos em páginas.")

    def update_page_size(value):
        set_page_size_text(value)
        if not filepath:
            return

        try:
            words = carrega_arquivo(filepath)
            created_pages = paginacao(words, tamanho_pagina(value))
        except ValueError as error:
            set_pages([])
            set_message(str(error))
            return

        set_total_words(len(words))
        set_pages(created_pages)
        set_message("Paginação atualizada.")

    def page_preview(page_number, records):
        preview = ", ".join(records[:5])
        return f"Página {page_number}: {preview}"

    with VBoxView():
        Label("Carga de dados e paginação")
        Label(f"Arquivo: {basename(filepath) if filepath else 'nenhum selecionado'}")
        with HBoxView():
            Label("Registros por página:")
            TextInput(
                text=page_size_text,
                placeholder_text="Ex.: 100",
                on_change=update_page_size,
            )
        Button("Selecione o arquivo", on_click=select_file)
        Label(message, word_wrap=True)
        Label(f"Total de palavras: {total_words}")
        Label(f"Total de páginas: {len(pages)}")
        if pages:
            Label(page_preview(1, pages[0]), word_wrap=True)
            if len(pages) > 1:
                Label(page_preview(len(pages), pages[-1]), word_wrap=True)


@component
def MainWindow(self):
    with Window(title="Simulador de Índice Hash Estático",
                _size_open=(800, 600)):
        Screen()


def create_app():
    return App(MainWindow()).start()

