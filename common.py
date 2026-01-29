import threading
from multiprocessing import Process
import time

def spawn_prey(shared, lock, n=1):
    from prey import prey_main
    import shared_state
    
    for _ in range(n):
        p = Process(target=prey_main, args=(shared, lock, shared_state.prey_pids))
        p.start()
        time.sleep(1)  


def spawn_predator(shared, lock, n=1):
    from predator import predator_main
    import shared_state
    
    for _ in range(n):
        p = Process(target=predator_main, args=(shared, lock, shared_state.predator_pids))
        p.start()
        time.sleep(1)  


def kill_prey(shared, lock, n=1):
    with lock:
        actual_kill = min(n, shared["prey_count"])
        shared['prey_count'] -= actual_kill
        return actual_kill


def kill_predator(shared, lock, n=1):
    with lock:
        actual_kill = min(n, shared["predator_count"])
        shared['predator_count'] -= actual_kill
        return actual_kill


def consume_grass(shared, lock, amount):
    with lock:
        taken = min(amount, shared['grass'])
        shared['grass'] -= taken
        return taken