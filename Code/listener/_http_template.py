from http.server import BaseHTTPRequestHandler
from utils.redteam_db import RedTeamDB
import utildata.status as status
import json
from utils.custom_print import print_error, print_info, print_ok


class Listener(BaseHTTPRequestHandler):
    NEW_AGENT = "/new"
    RESULT = "/result"
    CHECK = "/check"
    ID = None

    def log_message(self, format, *args):
        pass # We don't want logs

    def _set_response(self, type="'text/html'"):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
    def do_GET(self):
        self._set_response('application/json')
        agent_name= self.path.replace("/", "")
        rt_db = RedTeamDB.get_instance()
        agent = rt_db.get_agent_by_name(agent_name)
        try:
            agent_id = agent[0][0]
            rt_db.update_agent_pooling(agent_id)
            tasks = rt_db.get_task_for_agent(agent_id)
            if tasks:
                task = tasks[0]
                data = {"id": task[0], "command": task[1], "args": task[2], "pluginargs": task[3], "type": task[4]}
                rt_db.update_task_status(task[0], status.RUN)
                self.wfile.write(bytes(json.dumps(data, ensure_ascii=False), 'utf-8')) 
            else:
                data = {"id": 0, "command": "", "args": "", "type": ""}
                self.wfile.write(bytes(json.dumps(data, ensure_ascii=False), 'utf-8'))
        except:
            pass

    def do_POST(self):
        rt_db = RedTeamDB.get_instance()
        self._set_response()
        self.wfile.write(''.encode('utf-8'))
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length).decode(errors="ignore") 
        data_load = json.loads(data)
        if self.path == self.NEW_AGENT:
            print_info(f"\nNew agent with name {data_load['name']}")
            lhost, lport = self.server.server_address
            rhost, rport = self.client_address
            listener = rt_db.get_id_listener_from_addr(lhost, lport)
            if listener:
                listener_id = listener[0][0]
                rt_db.add_agent(data_load, listener_id, rhost)
        elif self.RESULT in self.path:
            task_id = data_load.get("task_id", None)
            error = data_load.get("error", None)
            output = data_load.get("output", None)
            new_status = status.DONE
            name_client = self.path.split("/")[2]
            header_text = f"Result from {name_client}"
            print("")
            print(header_text)
            print("-" * len(header_text))
            if error:
                new_status = status.ERROR
                output += f" {error}"
            print(output)
            if task_id:
                rt_db.add_result(task_id, str(output), new_status)
       
        # enter_input()