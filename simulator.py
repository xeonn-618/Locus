import numpy as np
from scipy.ndimage import gaussian_filter
import config

class Simulator():
    def __init__(self, grass) -> None:
        self.grass = grass # A 2-D matrix
        self.tick = 1 # Initial tick

    # Grow the grass by a random range
    def grow_grass(self):
        # Create the rng generator
        rng = np.random.default_rng()

        # Create a random noise growth map
        noise_map = rng.integers(low=0, high=config.grass_growth_max, size=self.grass.shape)

        # Smooth the noise
        growth_map = gaussian_filter(noise_map, sigma=config.sigma//2) # Smaller sigma to localize growth in smaller patches

        # Normalize the smooth map to prevent completely smooth plains for small growth factors
        growth_map = ((growth_map - growth_map.min()) / (growth_map.max() - growth_map.min()) * config.grass_growth_max).astype(int)

        # Add the growth map to the current grass map
        self.grass += growth_map

        # Clip all grass above grass_max_length
        self.grass = np.clip(self.grass, 0, config.grass_max_length)

    def run_tick(self):
        # Run tick
        print(f"Tick : {self.tick}")

        # Grow the grass
        self.grow_grass()

        # Update tick
        self.tick += 1
