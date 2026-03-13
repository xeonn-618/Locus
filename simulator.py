import numpy as np
from scipy.ndimage import gaussian_filter
import config

# Random Number Generator
rng = np.random.default_rng()

class Simulator():
    def __init__(self, N, grass, p) -> None:
        self.grass = grass # A 2-D matrix
        self.tick = 1 # Initial tick
        self.N = N

        # Allelic frequencies
        self.p, self.q = p, 1-p

        # Deer population
        # We keep track of individuals by their array index
        self.population_coords = rng.integers(0, grass.shape[0], size=(N,2)) # ndarray([[X1, Y1], [X2, Y2]])
        self.population_sex = np.random.choice( [0, 1], N) # 0: Female, 1: Male
        self.population_age = rng.integers(1, 10, size=N) # Assign random ages between 1 to 10
        self.population_energy = np.full(N, config.initial_energy) # Assign initial energy to each individual
        self.population_isPregnant = np.zeros(N, dtype=bool) # All starting individuals start off not pregnant
        self.population_mateable = (self.population_age >= config.maturity_age) & (~self.population_isPregnant) 
        self.population_genotype = rng.binomial(n=1, p=p, size=(N,2)) # 0: recessive allele, 1: dominant allele
        self.population_germ_genotype = np.copy(self.population_genotype) # Initialize the germ genotype to be same as parent in beginning

    # Grow the grass by a random range
    def grow_grass(self):
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
        print(f"| {self.tick:^9} | {self.N:^7} | {self.p:^7} |")

        # Grow the grass
        self.grow_grass()

        # Update tick
        self.tick += 1
