import socket
import json
import os
import shared_state 
import common
import time

HOST = "127.0.0.1"
PORT = 5000

def prey_main(shared, lock, prey_pids, energy_start=11, H=7, R=15):
    pid = os.getpid()

    msg = {
        "type": "register",
        "role": "prey",
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
            print(f"[PREY {pid}] is hungry")
            consumed = common.consume_grass(shared, lock, 10)
            energy += consumed
            print(f"[PREY {pid}] consumed {consumed} grass, energy now {energy}")

        # Reproduction
        if energy >= R:
            print(f"[PREY {pid}] reproduces")
            common.spawn_prey(shared, lock, n=1)
            energy //= 2  


        if energy <= 0:
            with lock:
                if shared["prey_count"] > 0:
                    shared["prey_count"] -= 1
                if pid in prey_pids:
                    prey_pids.remove(pid)
            print(f"[PREY {pid}] dies")
            running = False

        time.sleep(1)

if __name__ == "__main__":
    shared = shared_state.shared
    lock = shared_state.lock
    prey_pids = shared_state.prey_pids
    prey_main(shared, lock, prey_pids, energy_start=50, H=30, R=80)
