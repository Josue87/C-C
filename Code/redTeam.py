from os import system, name, walk, _exit, getcwd, chdir, sep, mkdir
from os.path import join, dirname, abspath, exists
from subprocess import Popen, PIPE
from utils.banner import banner
from utils.prompt import prompt
from utils.shell_options import ShellOptions
from utils.command_parser import CommandParser
from utils.custom_print import print_info
from utils.color_palette import ColorSelected, colors_terminal
from utils.redteam_db import RedTeamDB


class Shell():
    
    def __init__(self):
        """Shell class that runs the ReadTeam tool
        """
        # Check directory, we need to be in RedTeam directory
        home = dirname(abspath(__file__))
        if home != getcwd():
            chdir(home)

        self.command_parser = CommandParser()
        self.shell_options = ShellOptions.get_instance()
        self.color_selected = ColorSelected(colors_terminal["dark"])
        system('cls' if name=='nt' else 'clear')

    def console(self):
        """Runs the console
        """
        banner()
        while True:
            try:
                module_name = self.command_parser.get_module_name()
                options = self.shell_options.get_shell_options()
                user_input = prompt(options, module_name).strip(" ")
                self.command_parser.parser(user_input)
            except KeyboardInterrupt:
                print("CTRL^C")

if __name__ == "__main__":
    RedTeamDB.get_instance()
    system('cls' if name=='nt' else 'clear')
    Shell().console()
