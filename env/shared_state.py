from multiprocessing import Manager, Lock

def create_shared_state():
    manager = Manager()
    return {
        "data": manager.dict({
            "grass": 100.0,
            "prey_count": 0,
            "predator_count": 0,
            "drought": False
        }),
        "lock": Lock()
    }, manager
# creates a dict that processes can access freely