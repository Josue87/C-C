import importlib
from os import sep, listdir
from os.path import isfile, join, isdir
from utils.custom_print import print_error, print_info, print_ok
from utils.custom_exception import exception


#@exception("Error importing the module")
def load_module(path):
    """Custom function to load a new module
    Args:
        path (str): Path fo the module
    Returns:
        RedTeamModule: Module loaded
    """
    print_info('Loading module...')
    try:
        if "listener" in path:
            my_path = path
        elif not "modules" in path:
            my_path = "modules." + path
        else:
            my_path = path.replace("./", "")
        my_path = my_path.replace("/", ".")
        my_path = my_path.replace("\\", ".")
        module = importlib.import_module(my_path)
        print_ok('Module loaded!')
        return module.RedTeamModule()
    except Exception as e:
        print_error(e)
        return None

## From BoomER
def get_modules_from_path(path):
    modules = []
    for dir in listdir(path):
        child = join(path, dir)
        if isfile(child) and child.endswith('.py') and "_" not in child:
            child = child.split(sep)
            child.pop(0)
            child = "/".join(child)
            modules.append(child[:-3])
        elif isdir(child):
            modules.extend(get_modules_from_path(child))
    return modules
