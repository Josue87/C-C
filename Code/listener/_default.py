import threading
import multiprocessing
import ssl
import os
from modules._module import Module
from utils.enter import enter_input
from utils.redteam_db import RedTeamDB
from utils.custom_print import print_error, print_info, print_ok


class DefaultListener(Module):
    def __init__(self, information, options, listener, server_class, type_l, certificate=None):
        self.listener = listener
        self.server_class = server_class
        self.type_listener = type_l
        self.certificate = certificate
        # Constructor of the parent class
        super(DefaultListener, self).__init__(information, options)

    # This module must be always implemented, it is called by the run option
    def run(self):
        try:
            new_listener = multiprocessing.Process(name="listener", target=self.start_listener, args=(self.server_class, 
                                    self.listener, self.args["interface"], int(self.args["port"]), self.certificate))
            new_listener.start()  
        except Exception as e:
            print(e)
            print_error("The listener already exists ...")

    def start_listener(self, server_class, handler_class, address="0.0.0.0", port=8080, certificate=None): 
        try:
            server_address = (address, port)
            server = server_class(server_address, handler_class)
        
            if certificate:
                server.socket = ssl.wrap_socket(server.socket, keyfile=certificate + ".key", certfile=certificate + ".pem", server_side=True)
            print_info(f'\nStarting {self.type_listener} listener on {address}:{port}...')
            try:
                new_id = RedTeamDB.get_instance().add_listener(self.type_listener, self.args["interface"], int(self.args["port"]), os.getpid())
                server.serve_forever()
            except:
                pass
        except Exception as e:
            print_error(e)

