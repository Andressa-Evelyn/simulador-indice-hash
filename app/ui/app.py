from edifice import App, Label, Window, component, VBoxView, Button, use_state
from PySide6.QtWidgets import QFileDialog
from os.path import basename


@component
def Screen(self):
    filepath, set_filepath = use_state("")
    def select_file(event):
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Selecionar arquivo",
            "",
            "Arquivos de texto (*.txt);;Todos os arquivos (*)",
        )

        if not file_path:
            return

        set_filepath(file_path)

    with VBoxView():
        message = f"Arquivo selecionado {basename(filepath)}" if filepath else "Nenhum arquivo selecionado"
        Label(message)
        Button("Selecione o arquivo", on_click=select_file)


@component
def MainWindow(self):
    with Window(title="Simulador de Índice Hash Estático",
                _size_open=(800, 600)):
        Screen()


def create_app():
    return App(MainWindow()).start()

