import platform


def is_windows():
    return "windows" == platform.system().lower()

def is_linux():
    return "linux" == platform.system().lower()