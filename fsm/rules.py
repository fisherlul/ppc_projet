def compute_state(energy, H):
    if energy <= 0:
        return "DEAD"
    return "ACTIVE" if energy < H else "PASSIVE"