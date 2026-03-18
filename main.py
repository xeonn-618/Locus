import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import config
from simulator import Simulator
import animate



# Random number generator
rng = np.random.default_rng()

# Random grass noise
grass_noise = rng.integers(low=0, high=100, size=(config.matrix_size, config.matrix_size))

# Apply gaussion filter to noisy matrix to get a smooth field
grass_noise_smoothed = gaussian_filter(grass_noise, sigma=config.sigma)

# Normalize the smooth noise into integers
normalized =(grass_noise_smoothed - grass_noise_smoothed.min())/ (grass_noise_smoothed.max() - grass_noise_smoothed.min())
grass_matrix = (normalized * 100).astype(int)


# Create the simulation object
MySim = Simulator(config.initial_population_size, grass_matrix, config.initial_p)

if __name__ == '__main__':
    print(f"| {'Tick':^9} | {'N':^7} | {'p':^7} | {"Avg. Energy":^9} | {'Avg. Food':^5} | {'Avg. Age':^7} |")
    print("-" * 80)
    # Run the simulation and animation
    animate.run(MySim)
