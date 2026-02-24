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
    return os.path.join(get_base_path(), *dirs)


def get_save_path():
    if platform.system() == "Windows":
        base = os.getenv('APPDATA')
        app_name = "MyGame"
    elif platform.system() == "Darwin": # macOS
        base = os.path.expanduser("~/Library/Application Support")
        app_name = "MyGame"
    else: # Linux
        base = os.path.expanduser("~/.local/share")
        app_name = "mygame"
    dir_path = os.path.join(base, app_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path

