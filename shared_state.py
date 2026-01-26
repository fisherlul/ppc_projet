from multiprocessing import Manager, Lock

manager = None
shared = None
lock = None
prey_pids = None
predator_pids = None

def init_manager():
    """Initialize the multiprocessing manager and shared resources"""
    global manager, shared, lock, prey_pids, predator_pids
    
    manager = Manager()
    shared = manager.dict()
    lock = manager.Lock()
    prey_pids = manager.list()
    predator_pids = manager.list()
    
    # Initialize shared state
    shared["grass"] = 0
    shared["prey_count"] = 0
    shared["predator_count"] = 0
    shared["running"] = True
    shared["paused"] = False
    shared["drought"] = False
    
    return shared, lock, prey_pids, predator_pids