import threading
lock = threading.Lock()


def spawn_prey(shared,lock, n=1):
    with lock:
        shared['prey_count'] += n

def kill_prey(shared,lock, n=1):
    with lock:
        shared['prey_count'] -= n if shared["prey_count"] >= n else 0


def consume_grass(shared,lock, amount):
    with lock:
        taken = min(amount, shared['grass'])
        shared['grass'] -= taken
        return taken

