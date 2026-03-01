import sys
import platform
import os


def get_base_path():
    """
    Возвращает путь к корневой папке приложения.
    В режиме разработки: папка со скриптом.
    В режиме сборки: папка с .exe файлом.
    """
    if getattr(sys, 'frozen', False):
        # Запущено из скомпилированного .exe
        return os.path.dirname(sys.executable)
    else:
        # Запущено из IDE / исходного кода
        return os.path.dirname(os.path.abspath(__file__))


def resource_path(dirs: list):
    return os.path.join(get_base_path(), "assets", *dirs)


def save_path(dirs: list):
    return os.path.join(get_base_path(), "p_data", *dirs)

