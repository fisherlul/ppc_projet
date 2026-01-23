from multiprocessing import Process, Queue
from env import main as env_main
from display import main as display_main

def main():
    q_env_to_display = Queue()
    q_display_to_env = Queue()

    p_env = Process(target=env_main, args=(q_env_to_display, q_display_to_env))
    p_disp = Process(target=display_main, args=(q_env_to_display, q_display_to_env))

    p_env.start()
    p_disp.start()

    try:
        p_env.join()
        p_disp.join()
    except KeyboardInterrupt:
        print("\n[MAIN] Ctrl+C reçu → arrêt propre")
        # demander à env d'arrêter (si pas déjà fait)
        q_display_to_env.put({"type": "stop"})
        # éviter de rester bloqué
        p_env.join(timeout=2)
        p_disp.join(timeout=2)

if __name__ == "__main__":
    main()
