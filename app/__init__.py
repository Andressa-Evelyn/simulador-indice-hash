def main():
    try:
        from app.ui.app import create_app
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "As dependências da interface gráfica não estão instaladas. "
            "Execute: python -m pip install -e ."
        ) from error

    create_app()

