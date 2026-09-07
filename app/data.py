from pathlib import Path

def carrega_arquivo(caminho: str | Path) -> list[str]:
    """Carrega uma lista de palavras não vazias de um arquivo de texto UTF-8."""
    try:
        with Path(caminho).open("r", encoding="utf-8") as file:
            palavras = [line.strip() for line in file if line.strip()]
    except (OSError, UnicodeError) as error:
        raise ValueError("Não foi possível ler o arquivo selecionado.") from error

    if not palavras:
        raise ValueError("O arquivo está vazio ou não contém palavras válidas.")

    return palavras


def paginacao(registros: list[str], tamanho_pagina: int) -> list[list[str]]:
    """Divida os registros em páginas com `tamanho_pagina` registros cada."""
    if tamanho_pagina <= 0:
        raise ValueError("O tamanho da página deve ser maior que zero.")

    total_size = len(registros)
    pages = [
        []
        for _ in range((total_size + tamanho_pagina - 1) // tamanho_pagina)
    ]

    for index, value in enumerate(registros):
        page_index = index // tamanho_pagina
        pages[page_index].append(value)

    return pages
