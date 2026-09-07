from edifice import palette_edifice_dark, palette_edifice_light, theme_is_light, use_palette_edifice
from PySide6.QtGui import QPalette


def get_theme_palette() -> QPalette:
    """Retorna a paleta de cores Edifice conforme o tema ativo (claro ou escuro)."""
    return palette_edifice_light() if theme_is_light() else palette_edifice_dark()


def get_theme_colors() -> dict[str, str | bool]:
    """Retorna o mapeamento completo de cores e tokens ajustados ao tema ativo e à paleta do Edifice."""
    is_light = theme_is_light()
    palette = get_theme_palette()

    base_text = palette.color(QPalette.ColorRole.WindowText).name()
    base_window = palette.color(QPalette.ColorRole.Window).name()
    base_card = palette.color(QPalette.ColorRole.Base).name()

    if is_light:
        return {
            'is_light': True,
            'accent': '#0084d1',
            'accent_subtle': '#ddf4ff',
            'accent_border': '#b6e3ff',
            'success': '#1a7f37',
            'success_bg': '#dafbe1',
            'success_border': '#4ac26b',
            'danger': '#cf222e',
            'danger_bg': '#ffebe9',
            'danger_border': '#ff8182',
            'text': '#24292f' if base_text in ('#000000', '#3c3c3c') else base_text,
            'text_muted': '#57606a',
            'border': '#d0d7de',
            'border_subtle': '#e1e4e8',
            'card_bg': '#ffffff' if base_card in ('#f2f2f2', '#ffffff') else base_card,
            'bg_subtle': '#f6f8fa',
            'bg_alt': '#fcfcfc',
            'window_bg': base_window,
            'table_row_even': '#efefef',
            'table_row_odd': '#e4e7eb',
            'table_text': '#1f2328',
        }

    return {
        'is_light': False,
        'accent': '#38bdf8',
        'accent_subtle': '#0c2d6b',
        'accent_border': '#1d4ed8',
        'success': '#3fb950',
        'success_bg': '#0f3d1e',
        'success_border': '#238636',
        'danger': '#f85149',
        'danger_bg': '#491819',
        'danger_border': '#da3633',
        'text': '#e6edf3' if base_text in ('#ffffff', '#c8c8c8') else base_text,
        'text_muted': '#8b949e',
        'border': '#3e4451',
        'border_subtle': '#30363d',
        'card_bg': '#2b2d30' if base_card in ('#323232', '#282828') else base_card,
        'bg_subtle': '#22252a',
        'bg_alt': '#26292f',
        'window_bg': base_window,
        'table_row_even': '#2d3139',
        'table_row_odd': '#23272e',
        'table_text': '#e6edf3',
    }


def get_header_style() -> dict:
    colors = get_theme_colors()
    return {
        'font-size': '24px',
        'font-weight': 'bold',
        'color': colors['text'],
    }


def get_section_header_style() -> dict:
    colors = get_theme_colors()
    return {
        'font-size': '18px',
        'font-weight': 'bold',
        'color': colors['text'],
    }


def get_primary_button_style() -> dict:
    colors = get_theme_colors()
    return {
        'background-color': colors['accent'],
        'color': '#ffffff',
        'font-weight': 'bold',
        'padding': 4
    }


def get_secondary_button_style() -> dict:
    colors = get_theme_colors()
    return {
        'background-color': colors['bg_subtle'],
        'color': colors['text'],
        # 'border': f"1px solid {colors['border']}",
        'font-weight': '600',
        'padding': 4
    }


def get_card_style() -> dict:
    colors = get_theme_colors()
    return {
        'background-color': colors['card_bg'],
        'border': f"1px solid {colors['border']}",
        'border-radius': 8,
        'padding': 12,
        'margin': 4,
        'align': 'top',
    }


# Dicionários estáticos mantidos para compatibilidade retroativa
COLORS = get_theme_colors()
PRIMARY_BUTTON = get_primary_button_style()
SECONDARY_BUTTON = get_secondary_button_style()
HEADER = get_header_style()
SECTION_HEADER = get_section_header_style()
