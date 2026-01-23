import socket
import json
import os
import signal
import time
from multiprocessing import Manager, Lock, Process
from common import spawn_prey, kill_prey, consume_grass



TICK_SECONDS = 1
GRASS_GROWTH = 5

def socket_server(shared, lock):
    HOST = "127.0.0.1"
    PORT = 5000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()

    print(f"[ENV] socket listening on {HOST}:{PORT}")

    while True:
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

def main(q_env_to_display, q_display_to_env):
    manager = Manager()
    lock = Lock()
    shared = manager.dict()
    with lock:
        shared["predator_count"] = 0

    with lock:
        shared["drought"] = False
    DROUGHT_DURATION = 8
    drought_end_time = 0.0

    def drought_handler(sig, frame):
        nonlocal drought_end_time
        now = time.time()
        drought_end_time = now + DROUGHT_DURATION
        with lock:
            shared["drought"] = True
        print(f"\n[ENV] Sécheresse déclenchée pour {DROUGHT_DURATION} secondes (PID: {os.getpid()})")
    signal.signal(signal.SIGUSR1, drought_handler)
    print(f"[ENV] prêt. PID: {os.getpid()} (envoie SIGUSR1 pour sécheresse)")

    shared["grass"] = 0
    shared["running"] = True
    shared["prey_count"] = 20
    shared["predator_count"] = 5
    with lock:
        shared["paused"] = False

    socket_proc = Process(
        target=socket_server,
        args=(shared, lock)
    )
    socket_proc.daemon = True
    socket_proc.start()

    step = 0
    try:
        while True:
            step += 1
            now = time.time()
            # Lire commandes display -> env (non bloquant)
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
                 # fin de sécheresse ?
                if now >= drought_end_time:
                    with lock:
                        shared["drought"] = False

                # herbe pousse seulement si pas sécheresse
                with lock:
                    drought = shared["drought"]

                if not drought:
                    with lock:
                        shared["grass"] += GRASS_GROWTH

                if step % 3 == 0:
                    spawn_prey(shared, lock ,1)



                if shared["grass"] < 20:
                    kill_prey(shared, lock ,1)
                pass
            with lock:
                grass = shared["grass"]
                preys = shared["prey_count"]
                drought = shared["drought"]
                predators = shared["predator_count"]

            q_env_to_display.put({
                "type": "status",
                "step": step,
                "grass": grass,
                "preys": preys,
                "predators": predators,
                "drought": drought,
                "paused": paused,
            })



            time.sleep(TICK_SECONDS)
    except KeyboardInterrupt:
        print("\n[ENV] stop", 1)
        shared["running"] = False

if __name__ == "__main__":
    main()