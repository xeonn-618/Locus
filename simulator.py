import numpy as np
from scipy.ndimage import gaussian_filter
import config

class Simulator():
    def __init__(self, N, grass, p) -> None:
        self.grass = grass # A 2-D matrix
        self.tick = 1 # Initial tick
        self.N = N

        # Allelic frequencies
        self.p, self.q = p, 1-p

        # Random Number Generator
        self.rng = np.random.default_rng()

        # Generate moves array
        R = config.vision_radius
        dx = np.arange(-R, R+1)
        dy = np.arange(-R, R+1)
        xx, yy = np.meshgrid(dx, dy)
        self.moves = np.column_stack((xx.ravel(), yy.ravel()))
        
        # Sort the array so [0,0] is first element of array
        distances = np.abs(self.moves[:, 0]) + np.abs(self.moves[:, 1]) # |x| + |y| ; absolute dist
        self.moves = self.moves[np.argsort(distances)]


        # Deer population
        # We keep track of individuals by their array index
        self.population_coords = self.rng.integers(0, grass.shape[0], size=(N,2)) # ndarray([[X1, Y1], [X2, Y2]])
        self.population_sex = np.random.choice( [0, 1], N) # 0: Female, 1: Male
        self.population_age = self.rng.integers(1, 10, size=N) # Assign random ages between 1 to 10
        self.population_energy = np.full(N, config.initial_energy) # Assign initial energy to each individual
        self.population_isPregnant = np.zeros(N, dtype=bool) # All starting individuals start off not pregnant
        self.population_mateable = (self.population_age >= config.maturity_age) & (~self.population_isPregnant) 
        self.population_genotype = self.rng.binomial(n=1, p=p, size=(N,2)) # 0: recessive allele, 1: dominant allele
        self.population_germ_genotype = np.copy(self.population_genotype) # Initialize the germ genotype to be same as parent in beginning

        # Occupancy grid
        self.occupancy_grid = np.zeros(grass.shape, dtype=bool)

        # Update occupancy grid to randomly placed starting population
        self.occupancy_grid[self.population_coords[:, 0], self.population_coords[:, 1]] = True 



    # Grow the grass by a random range
    def grow_grass(self):
        # Create a random noise growth map
        noise_map = self.rng.integers(low=0, high=config.grass_growth_max, size=self.grass.shape)

        # Smooth the noise
        growth_map = gaussian_filter(noise_map, sigma=config.sigma//2) # Smaller sigma to localize growth in smaller patches

        # Normalize the smooth map to prevent completely smooth plains for small growth factors
        growth_map = ((growth_map - growth_map.min()) / (growth_map.max() - growth_map.min()) * config.grass_growth_max).astype(int)

        # Add the growth map to the current grass map
        self.grass += growth_map

        # Clip all grass above grass_max_length
        self.grass = np.clip(self.grass, 0, config.grass_max_length)

    def deer_move(self):

        # Create potential moves array for each deer via np broadcasting (N, 9, 2)
        potential_moves = self.population_coords[:, np.newaxis, :] + self.moves

        # Set limits to prevent going out of bounds
        max_x = self.grass.shape[0] - 1
        max_y = self.grass.shape[1] - 1
        potential_moves[:, :, 0] = np.clip(potential_moves[:,:,0], 0, max_x) # Clip all potential moves going out of bounds in X axis
        potential_moves[:, :, 1] = np.clip(potential_moves[:,:,1], 0, max_y) # Clip all potential moves going out of bounds in Y axis

        # Take the indicies and get food values at the possible positions
        x_indicies = potential_moves[:,:,0]
        y_indicies = potential_moves[:,:,1]
        
        # Food values (N, 9)
        food_values = self.grass[x_indicies, y_indicies]

        # Find index of highest grass value of 9 possible moves for every N
        best_moves_indicies = np.argmax(food_values, axis=1)

        # Find best coordinate to move for each N
        best_coords = potential_moves[np.arange(self.N), best_moves_indicies]
        
        # Find distance moved by each deer
        dist_moved = (np.abs(best_coords[:, 0] - self.population_coords[:, 0]) + 
                      np.abs(best_coords[:, 1] - self.population_coords[:, 1]))

        # Subtract the energy cost of moving from their energy pool
        self.population_energy -= (dist_moved * config.cost_move)

        # Move each deer to its new best coord
        self.population_coords = best_coords

    def run_tick(self):
        print(f"| {self.tick:^9} | {self.N:^7} | {self.p:^7} | {self.population_energy.mean():^9}")

        # Grow the grass
        self.grow_grass()

        # Move the deer
        self.deer_move()

        # Update tick
        self.tick += 1
