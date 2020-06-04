import time
from os import sep, mkdir
from os.path import exists
import sqlite3
import re
from utils.custom_print import print_error
from utils.custom_exception import exception
import utildata.status as status


class RedTeamDB:
    
    __instance = None
    schema = [
        f"CREATE TABLE listeners ( \
            id        INTEGER PRIMARY KEY AUTOINCREMENT, \
            type        VARCHAR NOT NULL, \
            interface VARCHAR NOT NULL, \
            port INT NOT NULL, \
            status      VARCHAR NOT NULL DEFAULT '{status.RUN}', \
            created     INT DEFAULT 0, \
            pid     INT NOT NULL \
        )",
        f"CREATE TABLE agents ( \
            id        INTEGER PRIMARY KEY AUTOINCREMENT, \
            name VARCHAR NOT NULL, \
            os VARCHAR NOT NULL, \
            arch VARCHAR NOT NULL, \
            username VARCHAR NOT NULL, \
            is_admin   INT NOT NULL DEFAULT 0, \
            computername VARCHAR NOT NULL, \
            av VARCHAR NOT NULL DEFAULT 'No', \
            created   INT NOT NULL DEFAULT 0, \
            pooling  VARCHAR NOT NULL ,\
            host  VARCHAR NOT NULL ,\
            status      VARCHAR NOT NULL DEFAULT '{status.ALIVE}', \
            listener_id    VARCHAR NOT NULL REFERENCES listeners(id)\
        )",
        f"CREATE TABLE tasks ( \
            id       INTEGER PRIMARY KEY AUTOINCREMENT, \
            command  VARCHAR NOT NULL, \
            args  VARCHAR, \
            plugin_args  VARCHAR, \
            status      VARCHAR NOT NULL DEFAULT '{status.WAIT}', \
            agent_id  INTEGER NOT NULL REFERENCES agents(id), \
            result      VARCHAR, \
            type      VARCHAR NOT NULL DEFAULT 'command' \
        )"
    ]

    @staticmethod
    def get_instance():
        if RedTeamDB.__instance == None:
            RedTeamDB()
        return RedTeamDB.__instance

    def __init__(self):
        if RedTeamDB.__instance == None:
            RedTeamDB.__instance = self
        name = "db/redteam.db"
        create = True
        if not exists(name):
            create = False

        dbh = sqlite3.connect(name, timeout=10)
        if dbh is None:
            print_error(f"Could not connect to internal database, and couldn't create {name}")
        else:
            dbh.text_factory = str
        
            self.conn = dbh
            self.dbh = dbh.cursor()

            # Now we actually check to ensure the database file has the schema set
            # up correctly.
            if not create:
                try:
                    self.create()
                except BaseException as e:
                    print_error(f"Tried to set up the RedTeam database schema, but failed: {e.args[0]}")

    # Create the back-end schema
    def create(self):
        try:
            for query in self.schema:
                self.dbh.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            print_error("SQL error encountered when setting up database: " + e.args[0])

    @exception("Error adding new listener")
    def add_listener(self, listener_type, interface, port, pid):
        query = "INSERT INTO listeners (type, interface, port, created, pid) \
                    VALUES (?, ?, ?, ?, ?)"
        values = (listener_type, interface, port, time.time(), pid)
        self.dbh.execute(query, values)
        lastid = self.dbh.lastrowid
        self.conn.commit()
        return lastid

    @exception("Error adding new agent")
    def add_agent(self, agent, listener_id, host):
        query = "INSERT INTO agents (name, os, arch, username, is_admin, computername, av, created, pooling, host, listener_id) \
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        created = time.time()
        values = (agent.get("name"), agent.get("os"), agent.get("arch"), agent.get("username"), agent.get("isadmin"), agent.get("computername"), 
                agent.get("av"), created, created, host, listener_id)
        self.dbh.execute(query, values)
        self.conn.commit()
    
    @exception("Error adding task")
    def add_task(self, agent_id, command, args="", plugin_args="", task_type="command"):
        query = "INSERT INTO tasks (command, args, plugin_args, agent_id, type) \
                    VALUES (?, ?, ?, ?, ?)"
        values = (command, args, plugin_args, agent_id, task_type)

        self.dbh.execute(query, values)
        self.conn.commit()
    
    @exception("Error adding result")
    def add_result(self, task_id, result, status):
        query = "UPDATE tasks SET result = ? WHERE id= ?"
        self.dbh.execute(query, (result, task_id))
        self.conn.commit()
        query = "UPDATE tasks SET status = ?  WHERE id= ?"
        self.dbh.execute(query, (status, task_id))
        self.conn.commit()

    @exception("Error updating status task")
    def update_task_status(self, task_id, status):
        query = "UPDATE tasks SET  status = ? WHERE id= ?"
        values = (status, task_id)
        self.dbh.execute(query, values)
        self.conn.commit()

    @exception("Error updating status agent")
    def update_agent_status(self, agent_id, status):
        query = "UPDATE agents SET  status=? WHERE id= ?"
        values = (status, agent_id)
        self.dbh.execute(query, values)
        self.conn.commit()
    
    @exception("Error updating status agent")
    def update_agent_pooling(self, agent_id):
        query = "UPDATE agents SET  pooling=? WHERE id= ?"
        pooling = time.time()
        values = (pooling, agent_id)
        self.dbh.execute(query, values)
        self.conn.commit()

    @exception("Error updating listener")
    def update_listener_status(self, l_id, status):
        query = "UPDATE listeners SET status = ? WHERE id= ?"
        values = (status, l_id)
        self.dbh.execute(query, values)
        self.conn.commit()

    @exception("Error getting listeners")
    def get_listeners(self):
        query = "SELECT * FROM listeners"
        self.dbh.execute(query)
        return self.dbh.fetchall()

    @exception("Error getting listener by id")
    def get_listener_by_id(self, l_id):
        query = "SELECT * FROM listeners WHERE id=?"
        self.dbh.execute(query, (l_id,))
        return self.dbh.fetchall()

    @exception("Error getting agents")
    def get_agents(self):
        query = "SELECT * FROM agents"
        self.dbh.execute(query)
        return self.dbh.fetchall()

    @exception("Error getting agent by name")
    def get_agent_by_name(self, name):
        query = "SELECT id FROM agents WHERE name=?"
        self.dbh.execute(query, (name,))
        return self.dbh.fetchall()

    @exception("Error getting agent by id")
    def get_agent_by_id(self, a_id):
        query = "SELECT id,name,status FROM agents WHERE id=?"
        self.dbh.execute(query, (a_id,))
        return self.dbh.fetchall()
    
    @exception("Error getting tasks")
    def get_tasks(self):
        query = "SELECT * FROM tasks"
        self.dbh.execute(query)
        return self.dbh.fetchall()

    @exception("Error getting listeners")
    def get_a_listener(self, l_id):
        query = "SELECT * FROM listeners WHERE id=?"
        self.dbh.execute(query, (l_id,))
        return self.dbh.fetchall()

    @exception("Error getting ID listener")
    def get_id_listener_from_addr(self, interface, port, status="Running"):
        query = "SELECT id FROM listeners WHERE interface = ? AND port = ? AND status = ?"
        self.dbh.execute(query, [interface, port, status])
        return self.dbh.fetchall()

    @exception("Error getting agents")
    def get_an_agent(self, a_id):
        query = "SELECT * FROM agents WHERE id=?"
        self.dbh.execute(query, (a_id,))
        return self.dbh.fetchall()
    
    @exception("Error getting tasks")
    def get_a_task(self, t_id):
        query = "SELECT * FROM tasks WHERE id=?"
        self.dbh.execute(query, (t_id,))
        return self.dbh.fetchall()

    @exception("Error getting tasks for agent")
    def get_task_for_agent(self, a_id):
        query = "SELECT id,command,args, plugin_args,type FROM tasks WHERE agent_id=? AND status=?"
        self.dbh.execute(query, (a_id, status.WAIT))
        return self.dbh.fetchall()

    @exception("Error removing a listener")
    def delete_listener(self, l_id):
        query = "DELETE FROM listeners WHERE id=?"
        self.dbh.execute(query, (l_id,))

    @exception("Error removing an agent")
    def delete_agent(self, a_id):
        query = "DELETE FROM agents WHERE id=?"
        self.dbh.execute(query, (a_id,))
        
    @exception("Error removing a task")
    def delete_task(self, t_id):
        query = "DELETE FROM tasks WHERE id=?"
        self.dbh.execute(query, (t_id,))