import socket
import json
import os
import shared_state
import common
import time

HOST = "127.0.0.1"
PORT = 5000

def predator_main(shared, lock, predator_pids, energy_start=20, H=5, R=25):
    pid = os.getpid()
    msg = {
        "type": "register",
        "role": "predator",
        "pid": pid
    }

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.send(json.dumps(msg).encode())

    s.close()

    energy = energy_start
    running = True

    while running and shared['running']:
        energy -= 5
        
        # Hunger
        if energy < H:
            print(f"[PREDATOR {pid}] is hungry")
            with lock:
                if shared['prey_count'] > 0:
                    shared['prey_count'] -= 1
                    energy += 15  # gain energy from hunting
                    print(f"[PREDATOR {pid}] hunted prey, energy now {energy}")
                else:
                    print(f"[PREDATOR {pid}] no prey available")

        # Reproduction
        if energy >= R:
            print(f"[PREDATOR {pid}] reproduces")
            common.spawn_predator(shared, lock, n=1)
            energy //= 2  # energy split between parent and offspring

        # Death
        if energy <= 0:
            with lock:
                if shared["predator_count"] > 0:
                    shared["predator_count"] -= 1
                if pid in predator_pids:
                    predator_pids.remove(pid)
            print(f"[PREDATOR {pid}] dies")
            running = False

        time.sleep(1)

if __name__ == "__main__":
    shared = shared_state.shared
    lock = shared_state.lock
    predator_pids = shared_state.predator_pids
    predator_main(shared, lock, predator_pids, energy_start=50, H=30, R=80)
