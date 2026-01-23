import time

def main(q_env_to_display, q_display_to_env):
    print("[DISPLAY] démarré (Ctrl+C pour quitter)")
    try:
        while True:
            # Lire tous les messages disponibles
            while not q_env_to_display.empty():
                msg = q_env_to_display.get()
                if msg.get("type") == "status":
                    print(
                        f"[DISPLAY] step={msg['step']} | grass={msg['grass']} | "
                        f"preys={msg['preys']} | predators={msg['predators']} | drought={msg['drought']} | paused={msg['paused']}"
                    )
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[DISPLAY] arrêt demandé")
        # Optionnel: demander à env de s'arrêter
        q_display_to_env.put({"type": "stop"})
