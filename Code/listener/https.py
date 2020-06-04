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
from subprocess import Popen, PIPE
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
        error = True
        command1 = "openssl req -new -newkey rsa:4096  -subj '/C=ES/ST=Denial/L=Madrdid/O=Dis/CN=evil.com' -nodes -keyout ./cert/redteam.key -out ./cert/redteam.csr"
        command2 ="openssl x509 -req -sha256 -days 365 -in ./cert/redteam.csr -signkey ./cert/redteam.key -out ./cert/redteam.pem"
        result = Popen(command1, stdout=PIPE,stderr=PIPE, shell=True)
        output = result.stdout.read().decode() + result.stderr.read().decode()
        if "writing new private key" in output:
            result = Popen(command2, stdout=PIPE,stderr=PIPE, shell=True)
            output = result.stdout.read().decode() + result.stderr.read().decode()
            if "Getting Private key" in output:
                print_ok("The certificate has been generated correctly")
                error = False

        if error:
            print_error("Error generating certificate to HTTPS listener")

        # Constructor of the parent class
        super(RedTeamModule, self).__init__(information, options, Listener, HTTPServer, "https", "./cert/redteam")
