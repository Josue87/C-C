from utils.redteam_db import RedTeamDB
from utils.custom_print import print_info, print_error, print_ok
import utildata.status as status


def is_agent_alive(func):
    """Decorator used to check if the current agent is alive
    
    Args:
        func (func): function passed to the decorator
    
    Returns:
        wrapper: decorator wrapped
    """
    def wrapper(*args):
        rt_db = RedTeamDB.get_instance()
        # Get agent ID from module
        a_id = args[0].args["agent"]
        result = rt_db.get_agent_by_id(a_id)
        if not result:
            print_error("The agent is not found. Check agent list")
            return
        elif result[0][2] !=  status.ALIVE:
            print_info("The agent may not respond")
        func(*args)
    return wrapper