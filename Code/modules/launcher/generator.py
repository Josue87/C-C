from modules._module import Module
from utils.custom_print import print_info, print_error, print_ok
from utildata.dataset_options import Option
from utils.shell_options import ShellOptions
from utils.redteam_db import RedTeamDB
from subprocess import Popen, PIPE
import utildata.status as status



class RedTeamModule(Module):

    def __init__(self):
        information = {"Name": "Generate a launcher",
                       "Description": "With this module you will be able to execute a command.",
                       "Author": "@josueencinar"}

        options = {
            "listener": Option.create(name="listener", description="Select the listener to connect", required=True),
            "launcher": Option.create(name="launcher", description="Wich Launcher do you want?", required=True),
            "destination": Option.create(name="destination", description="Path to save the file", value="./files/", required=True),
            }

        # Constructor of the parent class
        super(RedTeamModule, self).__init__(information, options)


    # Autocomplete set option with values    
    def update_complete_set(self):
        s_options = ShellOptions.get_instance()
        rt_db = RedTeamDB.get_instance()
        listeners = []

        for listener in rt_db.get_listeners():
            if listener[4] == status.RUN:
                listeners.append(f"{listener[0]} -- {listener[2]}:{listener[3]} ({listener[1]})")
        s_options.add_set_option_values("launcher", ["cs", "py"])

        s_options.add_set_option_values("listener", listeners)

    # This function must be always implemented, it is called by the run option
    def run(self):
        rt_db = RedTeamDB.get_instance()
        try:
            id_listener  = self.args["listener"].split(" -- ")[0]
            listener = rt_db.get_listener_by_id(int(id_listener))
            if not listener:
                raise Exception()
        except:
            print_error("Error getting listener")
            return
        listener = listener[0]
        name_file = "./launchers/" + listener[1] + "/Client." + self.args["launcher"]
        destination = self.args["destination"]
        if not destination.endswith("/"):
            destination += "/"
        destination +=  listener[1] + "_Client." + self.args["launcher"]
        try:
            f_r = open (name_file, "r")
            data = f_r.read()
            f_r.close()
            ip = listener[2]
            if listener[2] == "0.0.0.0":
                ip = input("Listener has interface 0.0.0.0, set your IP: ")
            data = data.replace("xx.xx.xx.xx", ip).replace("yyyy", str(listener[3]))
            with open (destination, "w") as f_w:
                f_w.write(data)
                print_info(f"The launcher has been generated in {destination}")

        except Exception as e:
            print_error(f"Something was wrong generating the launcher: {e}")   
      