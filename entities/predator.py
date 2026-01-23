# PREDATOR CLASS
from entities.animal import Animal
import configs as cfg

class Predator(Animal):
    def __init__(self, energy_start, H, R, shared):
        super().__init__(energy_start, H, R, shared)
        self.H = cfg.HUNGER_THRESHOLD_PREDATOR
        self.R = cfg.REPRODUCTION_THRESHOLD_PREDATOR
        self.data = shared["data"]
        
    def run(self):
        return super().run()
    
    def die(self):
        with self.lock:
            self.data["predator_count"] = max(0, self.data["predator_count"] - 1)
    
    def feed(self):
        with self.lock:
            if self.data["prey_count"] > 0:
                self.data["prey_count"] -= 1
                self.energy += 20 
                
    def reproduce(self):
        with self.lock:
            new_born = Predator(self.energy/2, self.H, self.R, self.shared)
            self.energy /= 2
            new_born.start()
            self.data["predator_count"] += 1