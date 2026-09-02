import sys
import os


def get_base_path():
    """
    Возвращает путь к корневой папке приложения.
    В режиме разработки: папка со скриптом.
    В режиме сборки: папка с .exe файлом.
    """
    if "__compiled__" in globals():
        # Запущено из скомпилированного Nuitka EXE
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    elif getattr(sys, 'frozen', False):
        # Запущено из PyInstaller-сборки (на будущее)
        return os.path.dirname(sys.executable)
    else:
        # Запущено из IDE / исходного кода
        return os.path.dirname(os.path.abspath(__file__))


def resource_path(dirs: list):
    return os.path.join(get_base_path(), "assets", *dirs)


def save_path(dirs: list):
    return os.path.join(get_base_path(), "p_data", *dirs)

