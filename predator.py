import socket
import json
import os
import shared_state
import common
import time

HOST = "127.0.0.1"
PORT = 5000

def predator_main(shared, lock, predator_pids, energy_start=60, H=40, R=85):
    pid = os.getpid()
    
    try:
        msg = {
            "type": "register",
            "role": "predator",
            "pid": pid
        }

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)  # Add timeout to prevent hanging
        s.connect((HOST, PORT))
        s.send(json.dumps(msg).encode())

        s.close()
        
        # ajoute le pid aux predateurs vivants
        with lock:
            if pid not in predator_pids:
                predator_pids.append(pid)
    except Exception as e:
        print(f"[PREDATOR {pid}] Failed to register: {e}")
        return 

    energy = energy_start
    running = True

    while running and shared['running']:
        # Hunger 
        if energy < H:
            print(f"[PREDATOR {pid}] is hungry (energy={energy})")
            with lock:
                # trouve une proie non chassée
                living_prey_pids = list(shared_state.prey_pids)
                hunted_list = list(shared_state.hunted_prey)  
                available_prey = [p for p in living_prey_pids if p not in hunted_list]
                
                if available_prey and shared['prey_count'] > 0:
                    hunted_pid = available_prey[0]
                    shared_state.hunted_prey.append(hunted_pid)  
                    energy += 50  
                else:
                    print(f"[PREDATOR {pid}] no prey available")
        
        # Lose energy for the tick
        energy -= 5

        # Reproduction
        if energy >= R:
            print(f"[PREDATOR {pid}] reproduces")
            common.spawn_predator(shared, lock, n=1)
            energy //= 2  

        # mort
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