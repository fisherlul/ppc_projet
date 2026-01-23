import multiprocessing
from fsm.rules import compute_state
from abc import ABC, abstractmethod
# import configs as cfg
import time

class Animal(multiprocessing.Process):
    def __init__(self, energy_start, H, R, shared, metabolism=20):
        super().__init__()
        self.energy = energy_start
        self.H = H
        self.R = R
        self.shared = shared
        self.metabolism = metabolism    # cost of staying alive
        self.lock = multiprocessing.Lock()
        
    def run(self):
        while self.energy > 0:
            self.energy -= self.metabolism
            state = compute_state(self.energy, self.H)
            
            if state == "ACTIVE":
                self.feed()
                
            if state == "DEAD":
                self.die()
                
            if self.energy > self.R:
                self.reproduce()
                
            time.sleep(0.5)
            
        self.die()
        
    @abstractmethod # requires children to define these methods
    def feed(self): pass

    @abstractmethod
    def reproduce(self): pass

    @abstractmethod
    def die(self): pass
        
# PREDATOR CLASS        
class Predator(Animal):
    def __init__(self, energy_start, H, R, shared):
        super().__init__(energy_start, H, R, shared)
        
    def run(self):
        return super().run()
    
    def die(self):
        with self.lock:
            self.shared["data"]["predator_count"] -= 1
    
    def feed(self):
        with self.lock:
            if self.shared["data"]["prey_count"] > 0:
                self.shared["data"]["prey_count"] -= 1
                self.energy += 20 # example of energy
                
    def reproduce(self):
        with self.lock:
            new_born = Predator(self.energy/2, self.H, self.R, self.shared)
            self.energy /= 2
            new_born.start()
            self.shared["data"]["predator_count"] += 1
    
# PREY CLASS
class Prey(Animal):
    def __init__(self, energy_start, H, R, shared):
        super().__init__(energy_start, H, R, shared)
        
    def run(self):
        return super().run()
    
    def die(self):
        with self.lock:
            self.shared["data"]["prey_count"] -= 1
            
    def feed(self):
        with self.lock:
            if self.shared["data"]["grass"] > 0:
                self.shared["data"]["grass"] -= 10
                self.energy += 30 # larger than predator, more likely to reproduce
            
    def reproduce(self):
        with self.lock:
            new_born = Prey(self.energy/2, self.H, self.R, self.shared)
            self.energy /= 2
            new_born.start()
            self.shared["data"]["prey_count"] += 1