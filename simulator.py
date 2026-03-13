import numpy as np

class Simulator():
    def __init__(self, grass) -> None:
        self.grass = grass # A 2-D matrix
        self.tick = 1 # Initial tick

    # Grow the grass by a random range
    def grow_grass(self):
        self.grass += np.random.randint(low=1, high=5, size=self.grass.shape)

    def run_tick(self):
        # Run tick
        print(f"Tick : {self.tick}")

        # Grow the grass
        self.grow_grass()

        # Update tick
        self.tick += 1
