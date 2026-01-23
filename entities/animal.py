import multiprocessing
from fsm.rules import compute_state
from abc import abstractmethod
# import configs as cfg
import time

class Animal(multiprocessing.Process):
    def __init__(self, energy_start, H, R, shared, metabolism=5):
        super().__init__()
        self.energy = energy_start
        self.H = H
        self.R = R
        self.shared = shared
        self.metabolism = metabolism    # cost of staying alive
        self.lock = shared["lock"]
        self.data = shared["data"]

    def run(self):
        while self.energy > 0:
            self.energy -= self.metabolism
            state = compute_state(self.energy, self.H)

            print(f"[{self.name}] Energy: {self.energy} | State: {state}")
            
            if state == "ACTIVE":
                self.feed()

            elif state == "PASSIVE":
                pass
                
            elif state == "DEAD":
                break

            else: 
                raise ValueError(f"Invalid state: {state}")
                
            if self.energy > self.R:
                self.reproduce()
                
            time.sleep(10)
            
        self.die()
        
    @abstractmethod # requires children to define these methods
    def feed(self): pass

    @abstractmethod
    def reproduce(self): pass

    @abstractmethod
    def die(self): pass
        

    
