from entities.animal import Animal
import configs as cfg

class Prey(Animal):
    def __init__(self, energy_start, H, R, shared):
        super().__init__(energy_start, H, R, shared)
        self.H = cfg.HUNGER_THRESHOLD_PREY
        self.R = cfg.REPRODUCTION_THRESHOLD_PREY
        
    def run(self):
        return super().run()
    
    def die(self):
        with self.lock:
            self.data["prey_count"] = max(0, self.data["prey_count"] - 1)
            
    def feed(self):
        print(f"Prey {self.name} is attempting to feed...") # DEBUG
        with self.lock:
            if self.data["grass"] > 0:
                eat = min(10, self.data["grass"])
                self.data["grass"] -= eat

                self.energy += 30 # larger than predator, more likely to reproduce
                print(f"Prey ate. Grass remaining: {self.data['grass']}") # DEBUG
            
    def reproduce(self):
        with self.lock:
            new_born = Prey(int(self.energy//2), self.H, self.R, self.shared)
            self.energy /= 2
            new_born.start()
            self.data["prey_count"] += 1