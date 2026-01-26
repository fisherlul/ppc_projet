import socket
import json
import os
import signal
import time
from multiprocessing import Manager, Lock, Process
from common import spawn_prey, kill_prey, consume_grass, spawn_predator, kill_predator
from prey import prey_main
from predator import predator_main
import shared_state

TICK_SECONDS = 1
GRASS_GROWTH = 15

def socket_server(shared, lock):
    HOST = "127.0.0.1"
    PORT = 5000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()

    print(f"[ENV] socket listening on {HOST}:{PORT}")

    while shared.get("running", True):
        conn, addr = s.accept()
        data = conn.recv(1024).decode()

        try:
            msg = json.loads(data)
            if msg["type"] == "register":
                role = msg["role"]
                pid = msg["pid"]

                with lock:
                    if role == "prey":
                        shared["prey_count"] += 1
                    elif role == "predator":
                        shared["predator_count"] += 1

                print(f"[ENV] {role} joined (pid={pid})")

                conn.send(json.dumps({"status": "ok"}).encode())
        except Exception as e:
            print("[ENV] socket error:", e)

        conn.close()

def main(q_env_to_display=None, q_display_to_env=None):
    shared, lock, prey_pids, predator_pids, hunted_prey = shared_state.init_manager()

    shared_state.shared = shared
    shared_state.lock = lock
    shared_state.prey_pids = prey_pids
    shared_state.predator_pids = predator_pids
    shared_state.hunted_prey = hunted_prey
    
    with lock:
        shared["prey_count"] = 0
        shared["predator_count"] = 0
        shared["drought"] = False
        shared["grass"] = 200
        shared["running"] = True
        shared["paused"] = False

    DROUGHT_DURATION = 8
    drought_end_time = 0.0

    def drought_handler(sig, frame):
        nonlocal drought_end_time
        now = time.time()
        drought_end_time = now + DROUGHT_DURATION
        with lock:
            shared["drought"] = True
        print(f"\n[ENV] Secheresse declenchee pour {DROUGHT_DURATION} secondes (PID: {os.getpid()})")
    
    signal.signal(signal.SIGUSR1, drought_handler)
    print(f"[ENV] pret. PID: {os.getpid()} (envoie SIGUSR1 pour secheresse)")

    socket_proc = Process(
        target=socket_server,
        args=(shared, lock)
    )
    socket_proc.daemon = True
    socket_proc.start()
    
    # temps pour initialiser le socket server
    time.sleep(2)

    step = 0
    # initialise quelques proies et predateurs
    spawn_prey(shared, lock, n=5)
    time.sleep(1)
    
    spawn_predator(shared, lock, n=3)
    time.sleep(1)

    
    try:
        while True:
            step += 1
            now = time.time()
            
            # Lire commandes display -> env (non bloquant)
            if q_display_to_env is not None:
                while not q_display_to_env.empty():
                    cmd = q_display_to_env.get()
                    if cmd.get("type") == "pause":
                        with lock:
                            shared["paused"] = True
                    elif cmd.get("type") == "resume":
                        with lock:
                            shared["paused"] = False
                    elif cmd.get("type") == "stop":
                        with lock:
                            shared["running"] = False
            
            with lock:
                paused = shared["paused"]
            
            if not paused:
                # fin de secheresse ?
                if now >= drought_end_time:
                    with lock:
                        shared["drought"] = False

                # herbe pousse seulement si pas secheresse
                with lock:
                    drought = shared["drought"]

                if not drought:
                    with lock:
                        shared["grass"] += GRASS_GROWTH

                # if step % 3 == 0:
                #     with lock:
                #         if shared["prey_count"] < 30:
                #             spawn_prey(shared, lock, n=1)

                # Kill excess prey if resources are scarce
                with lock:
                    grass_amt = shared["grass"]
                    prey_amt = shared["prey_count"]
                    if grass_amt < 20 and prey_amt > 20:
                        kill_prey(shared, lock, 1)

                # Spawn new predators occasionally if population is low
                hunted = list(shared_state.hunted_prey)
                if step % 5 == 0:
                    with lock:
                        if shared["predator_count"] < 10 and shared["prey_count"] > 10:
                            spawn_predator(shared, lock, n=1)

            with lock:
                grass = shared["grass"]
                preys = shared["prey_count"]
                drought = shared["drought"]
                predators = shared["predator_count"]
                
            # Check for extinction
            if preys <= 0 and predators <= 0:
                print("\n[ENV] Both populations extinct - simulation ending")
                with lock:
                    shared["running"] = False
                break

            if q_env_to_display is not None:
                q_env_to_display.put({
                    "type": "status",
                    "step": step,
                    "grass": grass,
                    "preys": preys,
                    "predators": predators,
                    "drought": drought,
                    "paused": paused,
                })
            
            # Print status to console
            print(f"[ENV] Step {step}: Grass={grass}, Prey={preys}, Predators={predators}, Drought={drought}")

            time.sleep(TICK_SECONDS)
    except KeyboardInterrupt:
        print("\n[ENV] stop")
        with lock:
            shared["running"] = False
            
    finally:
        print("[ENV] Cleaning up...")
        with lock:
            shared["running"] = False
        socket_proc.join(timeout=2)
        if socket_proc.is_alive():
            socket_proc.terminate()
        print("[ENV] Shutdown complete")

if __name__ == "__main__":
    main()