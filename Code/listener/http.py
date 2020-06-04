import re
import threading
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from modules._module import Module
from listener._default import DefaultListener
from utildata.dataset_options import Option
from utils.custom_print import print_error, print_info, print_ok
from utils.enter import enter_input
from utils.redteam_db import RedTeamDB
import utildata.status as status
from listener._http_template import Listener


class RedTeamModule(DefaultListener):
    def __init__(self):
        information = {"Name": "Red listener",
                       "Description": "HTTP Listener to connect Agents",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"port": Option.create(name="port", description="Listener Port", value="8080", required=True),
                   "interface": Option.create(name="interface", description="Listener Address", value="0.0.0.0", required=True),
                   "src": Option.create(name="src", description="Path", value="/", required=False)}

        # Constructor of the parent class
        super(RedTeamModule, self).__init__(information, options, Listener, HTTPServer, "http")
