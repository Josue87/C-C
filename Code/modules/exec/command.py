from modules._module import Module
from utils.custom_print import print_info, print_error, print_ok
from utildata.dataset_options import Option
from time import sleep
from os import sep
from utils.redteam_db import RedTeamDB
from utils.check_agent import is_agent_alive


class RedTeamModule(Module):

    def __init__(self):
        information = {"Name": "Execute a command",
                       "Description": "With this module you will be able to execute a command.",
                       "Author": "@josueencinar"}

        options = {
            "command": Option.create(name="command", required=True),
            "agent": Option.create(name="agent", required=True)
            }

        # Constructor of the parent class
        super(RedTeamModule, self).__init__(information, options)

    @is_agent_alive
    def run(self):
        rt_db = RedTeamDB.get_instance()
        rt_db.add_task(self.args["agent"], self.args["command"])
        print_info("Running Module")
      