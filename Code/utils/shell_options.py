from os import walk, sep
from os.path import join
from utils.color_palette import colors_terminal


class ShellOptions:
    __instance = None

    @staticmethod
    def get_instance():
        if ShellOptions.__instance == None:
            ShellOptions()
        return ShellOptions.__instance

    def __init__(self):
        if ShellOptions.__instance == None:
            ShellOptions.__instance = self
            modules_list = self._get_list_modules()
            all_list = self._get_list_listener()
            all_list.extend(modules_list)

            self.options_to_del = ["set", "unset", "show", "back", "run", "global"]
            self.shell_options = {  
                "load": all_list,
                "help": [],
                "banner": [],
                "find": [],
                "import": [],
                "export": [],
                "listeners": ["list", "kill"],
                "agents": ["list", "kill"],
                "modules": list(set([module.split(sep)[0] for module in modules_list])),
                "tasks": ["list", "kill"],
                "theme": colors_terminal.keys(),
                "exit": None,
                "quit": None
            }
    
    def get_shell_options(self):
        return self.shell_options
    
    # To allow extend autocomplete from modules
    def add_set_option_values(self, op, value):
        if type(value) != type([]):
            value = [value]
        try:
            self.shell_options["set"][op].append(value)
        except Exception as e:
            print(e)
    
    # To extend options to Autocomplete commands
    def add_module_options(self, options_name=[], new_functions=[]):
        self.shell_options["set"] = self.shell_options["global"]  = {}
        self.shell_options["unset"] = options_name
        for name in options_name:
            self.shell_options["set"][name] = self.shell_options["global"][name]  = []
        self.shell_options["run"] = []
        self.shell_options["back"] = []
        self.shell_options["show"] = ["options", "info"]
        # Update new functions
        for f in new_functions:
            if f not in list(self.shell_options.keys()):
                self.shell_options[f] = []
                self.options_to_del.append(f)
            
    def del_module_options(self):
        self.shell_options["show"] = ["banner"]
        for c in self.options_to_del:
            try:
                del self.shell_options[c]
            except:
                self.options_to_del.remove(c)
    
    # Search tool modules in folder 'modules'
    def _get_list_modules(self, pwd="modules"):
        file_list = []
        for (p, d, files) in walk(pwd):
            file_list.extend([join(p.replace("modules" + sep, ""), f.replace(".py", "")) for f in files if ("_" not in f) and ("_" not in p)])
        return file_list
    
    def _get_list_listener(self, pwd="listener"):
        file_list = []
        for (p, d, files) in walk(pwd):
            file_list.extend([join(p, f.replace(".py", "")) for f in files if ("_" not in f) and ("_" not in p)])
        return file_list
