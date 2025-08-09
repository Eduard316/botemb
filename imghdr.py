# imghdr.py - compat shim para Python 3.13
# python-telegram-bot==13.15 importa 'imghdr', pero fue eliminado de la stdlib en 3.13.
# Este módulo reemplaza la función what() usando 'filetype'.
import filetype

def what(file, h=None):
    """Devuelve etiquetas tipo 'jpeg', 'png', 'gif', etc., o None si no se detecta."""
    try:
        if h is not None:
            kind = filetype.guess(h)
        else:
            with open(file, "rb") as f:
                kind = filetype.guess(f.read(261))
        return kind.extension if kind else None
    except Exception:
        return None
