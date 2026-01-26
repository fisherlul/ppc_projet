import socket
import json
import os
import shared_state 
import common
import time

HOST = "127.0.0.1"
PORT = 5000

def prey_main(shared, lock, prey_pids, energy_start=60, H=40, R=75):
    pid = os.getpid()

    try:
        msg = {
            "type": "register",
            "role": "prey",
            "pid": pid
        }

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)  
        s.connect((HOST, PORT))
        s.send(json.dumps(msg).encode())

        s.close()
        
        # ajoute le pid aux proies vivantes
        with lock:
            if pid not in prey_pids:
                prey_pids.append(pid)
    except Exception as e:
        print(f"[PREY {pid}] Failed to register: {e}")
        return  

    energy = energy_start
    running = True

    while running and shared['running']:
        with lock:
            hunted_prey_list = list(shared_state.hunted_prey) 
            
        if pid in hunted_prey_list:
            print(f"[PREY {pid}] I'm in the hunted list! Dying now...")
            with lock:
                if shared["prey_count"] > 0:
                    shared["prey_count"] -= 1
                if pid in prey_pids:
                    prey_pids.remove(pid)
            break  
        
        # Lose energy for the tick
        energy -= 5
        
        # faim
        if energy < H:
            print(f"[PREY {pid}] is hungry (energy={energy})")
            consumed = common.consume_grass(shared, lock, 45)
            energy += consumed
            print(f"[PREY {pid}] consumed {consumed} grass, energy now {energy}")

        # Reproduction
        if energy >= R:
            print(f"[PREY {pid}] reproduces (energy={energy})")
            common.spawn_prey(shared, lock, n=1)
            energy //= 2  
            print(f"[PREY {pid}] energy after reproduction: {energy}")

        # mort
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