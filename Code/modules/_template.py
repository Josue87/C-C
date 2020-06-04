import requests
import pychromecast
from modules._module import AgentModule
from utils.custom_print import print_info, print_error
from utildata.dataset_options import Option
from utils.check_agent import is_agent_alive


class RedTeamModule(AgentModule):

    def __init__(self):
        information = {"Name": "Module Name",
                       "Description": "Module Description",
                       "Author": "@author"}

        options = {"option1": Option.create(name="option_name", value="default value", required="required?")}

        # Constructor of the parent class
        super(RedTeamModule, self).__init__(information, options)

    # This function must be always implemented, it is called by the run option
    @is_agent_alive
    def run(self):
        print("I'm a template")
        # Implement this function to launch module
        result = {
            "data": "TEST",
            "status": "OK" # OK, KO, Error, Review report
        }
        return result
    
    # If you need auxiliary functions, you can write the ones you want