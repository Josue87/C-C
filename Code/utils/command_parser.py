from os import _exit, walk, sep
from os.path import join
from datetime import datetime
from subprocess import Popen, PIPE
from utils.shell_options import ShellOptions
from utils.dynamic_load import load_module
from utils.custom_exception import exception
from utils.custom_print import  print_info, print_error, print_ok
from utils.banner import banner
from utils.global_list import Global
from utils.help import show_help
from utils.find import Find
from utils.color_palette import ColorSelected, colors_terminal
from utils.redteam_db import RedTeamDB
import utildata.status as STATUS
from os import kill
import signal
import time
from termcolor import cprint
import colorama
colorama.init()


class CommandParser:
    def __init__(self):
        self.module = None
        self.module_commands = ["set", "unset", "back", "show", "run", "global"]
        # Our switcher
        self.commands = {
            "load": self._load,
            "help": self._help,
            "banner": self._banner,
            "find": self._find,
            "modules": self._list_modules,
            "listeners": self._listener,
            "agents": self._agent,
            "theme": self._load_theme,
            "tasks": self._task,
            "exit": self._exit,
            "quit": self._exit,
        }
        self.shell_options = ShellOptions.get_instance()
    
    # 'command' is the user input
    @exception("Error parsing input")
    def parser(self, command):
        if not command:
            return

        if command.startswith("#"):
            self._execute_command(command[1:])
        else:
            u_input = command.split()
            if len(u_input) >=  2:
                self.commands.get(u_input[0])(u_input[1:])
            else:
                self.commands.get(u_input[0])()
    
    def update_module(self, value):
        self.module = value

    def get_module_name(self):
        name = ""
        if self.module:
            name = self.module.get_module_name()
        return name
    
    def _exit(self, param=None):
        print_info("Stopping tasks and listeners... ")
        db = RedTeamDB.get_instance()
        listeners = db.get_listeners()
        if listeners:
            for listener in listeners:
                pid = listener[-1]
                l_status = listener[4]
                self._kill_listener(l_status, pid)
                db.update_listener_status(listener[0], STATUS.STOP)
        tasks = db.get_tasks()
        if tasks:
            for task in tasks:
                t_status = task[4]
                if t_status != STATUS.DONE and t_status != STATUS.ERROR:
                    db.update_task_status(task[0], STATUS.UNFINISH)
        agents = db.get_agents()
        if agents:
            for agent in agents:
                db.update_agent_status(agent[0], STATUS.DEATH)
        print_info("Bye...")
        _exit(0)

    # Execute a system command
    @exception("Error Executing OS Command")
    def _execute_command(self, command):
        data = Popen(command, shell=True, stdout=PIPE).stdout.read()
        print("")
        print(data.decode(errors="ignore"))

    def _load_theme(self, theme):
        theme = colors_terminal.get(theme[0], None)
        if theme is not None:
            ColorSelected(theme)
            print_ok("Theme changed!")
        else:
            print_error("Theme not available")


    def _load(self, name):
        try:
            loaded = load_module(name[0])
        except Exception as e:
            print(e)
        if loaded:
            self._unload()
            self.module = loaded
            self.module.set_name(name[0])
            new_functions = self.module.get_new_functions()
            self.shell_options.add_module_options(self.module.get_options_names(), new_functions)
            # Add new commands to autocomplete
            module_new_commands = {
                "set": self.module.set_value,
                "global": self._setglobal,
                "unset": self.module.unset,
                "back": self._unload,
                "show": self.module.show,
                "run": self._run
            }

            for f in new_functions:
                if f not in list(module_new_commands.keys()):
                    module_new_commands[f] = getattr(self.module, f)
                    self.module_commands.append(f)

            self.commands.update(module_new_commands) 
            self.module.update_complete_set()
            
    @exception("")    
    def _unload(self):
        self.module = None
        # Remove commands that cannot be used without a module
        self.shell_options.del_module_options()
        for c in self.module_commands:
            try:
                del self.commands[c]
            except:
                 self.module_commands.remove(c)
        for f in self.module.get_new_functions():
            del self.commands[f]
    
    @exception("Error setting global option")
    def _setglobal(self, user_input=[]):
        if user_input and self.module:
            success = self.module.set_value(user_input)
            if success:
                Global.get_instance().add_value(user_input[0], ' '.join([str(x) for x in user_input[1:]]))
            
    @exception("There are required options without value")  
    def _run(self):
        if not self.module.check_arguments():
            raise("")
        try:
            result = self.module.run()
            if not result:
                return  
            l_status = result["status"]
        except Exception as e:
            print(e)
            l_status = "error"

    def _fill(self, param=None):
        Global.get_instance().load_configuration()
    
    def _save(self, param=None):
        Global.get_instance().save_configuration()

    def _banner(self, param=None):
        banner(animation=False)     
        
    def _help(self, param=None):
        data = None
        if self.module:
            data = self.module.get_extra_help()
        show_help(data)

    # TODO: Review Windows
    def _list_modules(self, category=None):
        pwd = "modules"
        if category != None:
            pwd += sep + category[0]
        print("")
        msg = "Modules list                     "
        print(msg)
        print("-"*len(msg))
        total = 0
        for (p, d, files) in walk(pwd):
            for f in files:
                 if ("_" not in f) and ("_" not in p):
                     print_info(join(p.replace("modules" + sep, ""), f.replace(".py", "")))
                     total += 1
        print("-"*len(msg))
        print_info(f"Modules count: <b>{total}</b>")
        print("")

    def _find(self, word=""):
        word = ' '.join(word).lower()
        data = f"Searching: {word}"
        print_info(data)
        print("-"*len(data))
        modules = Find().search(word)
        if not modules:
            print_info("No found")
            return
        for module in modules:
            print_info(module)
        print("-"*len(data))
        print_info(f"Modules count: <b>{len(modules)}</b>")
    
    def _task(self, params):
        db = RedTeamDB.get_instance()
        if "list" in params:
            """
            id       INTEGER PRIMARY KEY AUTOINCREMENT, \
            command  VARCHAR NOT NULL, \
            status      VARCHAR NOT NULL DEFAULT 'Waiting', \
            agent_id  INTEGER NOT NULL REFERENCES agents(id), \
            result   
            """
            tasks = db.get_tasks()
            for task in tasks:
                func = task[1]
                if task[2]:
                    if len(task[2]) > 80:
                        params = task[2][:80] + " ..."
                    else:
                        params = task[2]
                    func += f"({params})"
                print(f"{task[0]} - {func} - (agent_id: {task[5]}):")
                if task[4] == STATUS.DONE:
                    print_info(f"|_ Result: {task[6]}")
                elif task[4] == STATUS.ERROR:
                    print_error("|_ Error executing")
                elif task[4] == STATUS.UNFINISH:
                    print_error("|_ Unfinished")
                else:
                    print_info("|_ Waiting for result")
        elif "kill" in params and len(params) >= 2:
            task_id = params[1]
            task = db.get_a_task(task_id)
            if task:
                db.delete_task(task_id)
                print_info(f"Deletend {task_id}")
            else:
                print_error("No found task")

    def _agent(self, params):
        db = RedTeamDB.get_instance()
        if "list" in params:
            agents = db.get_agents()
            for agent in agents:
                #update status
                pooling = float(agent[9])
                now = time.time()
                rest = now-pooling
                color = "green"
                a_status = STATUS.ALIVE
                if rest > 60:
                    color = "red"
                    a_status = STATUS.DEATH
                elif rest > 30:
                    color = "yellow"
                    a_status = STATUS.UNKNOWN
                if a_status != agent[11]:
                    db.update_agent_status(agent[0], a_status)
                print(f"{agent[0]} - {agent[1]} (listener {agent[-1]}) - " , end="")
                cprint(a_status, color, end="")
                print(f" - {agent[2]}:{agent[3]} - {agent[4]}", end="")
                if agent[5] == 1:
                    cprint(" *", "green", end="")

                print("")

        elif "kill" in params and len(params) >= 2:
            agent_id = params[1]
            agent = db.get_an_agent(agent_id)
            if agent:
                db.delete_agent(agent_id)
                print_info(f"Killed {agent_id}")
            else:
                print_error("No found listener")

    def _listener(self, params):
        db = RedTeamDB.get_instance()
        if "list" in params:
            listeners = db.get_listeners()
            for listener in listeners:
                timestamp = str(listener[5]).split(".")[0]
                l_status = listener[4]
                color = "green"
                if l_status == STATUS.STOP:
                    color = "red"
                print(f"{listener[0]} - {listener[2]}:{listener[3]} - {listener[1]} ", end="")
                cprint(f"({l_status})", color, end="")
                print(f" - {datetime.fromtimestamp(int(timestamp))}")
        elif "kill" in params and len(params) >= 2:
            listener_id = params[1]
            listener = db.get_a_listener(listener_id)
            if listener:
                pid = listener[0][-1]
                l_status = listener[0][4]
                self._kill_listener(l_status, pid)
                db.delete_listener(listener_id)
                print_info(f"Killed {listener_id}")
            else:
                print_error("No found listener")
    
    def _kill_listener(self, l_status, pid):
        if l_status == STATUS.RUN:
            try:
                kill(pid, signal.SIGINT)
            except:
                pass

    