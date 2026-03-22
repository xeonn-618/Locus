import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.spatial import KDTree
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
        self.population_age = self.rng.integers(1, 9*config.year, size=(N,)) # Assign random ages between 1 to 10
        self.population_energy = np.full(N, config.initial_energy) # Assign initial energy to each individual
        self.population_isPregnant = np.zeros(N, dtype=bool) # All starting individuals start off not pregnant
        self.population_mateable = (self.population_age >= config.maturity_age) & (~self.population_isPregnant) & (self.population_energy > config.cost_mate)
        self.population_genotype = self.rng.binomial(n=1, p=p, size=(N,2)) # 0: recessive allele, 1: dominant allele
        self.population_germ_genotype = np.copy(self.population_genotype) # Initialize the germ genotype to be same as parent in beginning
        self.population_embryo_dict = np.zeros(shape=(N,3)) # N rows; [ageToBirth, allele1, allele2]
        
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

        # Implement random wander
        is_wandering = self.rng.random(self.N) < config.exploration_rate

        # Generate random wander indicies
        random_move_indicies = self.rng.integers(0, len(self.moves), size=self.N)

        # Find final moves
        final_move_indicies = np.where(is_wandering, random_move_indicies, best_moves_indicies)

        # Find best coordinate to move for each N
        best_coords = potential_moves[np.arange(self.N), final_move_indicies]
        
        # Find distance moved by each deer
        dist_moved = (np.abs(best_coords[:, 0] - self.population_coords[:, 0]) + 
                      np.abs(best_coords[:, 1] - self.population_coords[:, 1]))

        # Subtract the energy cost of moving from their energy pool
        self.population_energy -= (dist_moved * config.cost_move)

        # Subtract the metabolic cost from energy pool
        self.population_energy -= config.cost_metabolic

        # Move each deer to its new best coord
        self.population_coords = best_coords

    def deer_eat(self):
        x_coords = self.population_coords[:, 0]
        y_coords = self.population_coords[:, 1]

        available_grass = self.grass[x_coords, y_coords]

        # Array of amount of grass eaten by each deer
        grass_eaten = np.minimum(available_grass, config.max_eat)

        # Add energy of eaten grass to individuals
        self.population_energy += (grass_eaten * config.digestion_efficency).astype(int)

        # Remove the eaten grass
        self.grass[x_coords, y_coords] -= grass_eaten

        # Set negative grass lengths to zero
        self.grass[x_coords, y_coords] = np.clip(self.grass[x_coords, y_coords], 0, None)

    def deer_age(self):
        self.population_age += 1

    def deer_breed(self):
        # Use a KDTree data structure to efficiently search for the nearest deer
        # Create the tree object
        tree = KDTree(data=self.population_coords)
        
        # Query the tree to get the nearest neighbours of each deer
        # Set a limit to see if deers are within mating range
        nearest_neighbours = tree.query_pairs(r=config.mating_dist)
        
        # Iterate over each pair
        seen_deer_pairs = set()


        self.population_mateable = (self.population_age >= config.maturity_age) & (~self.population_isPregnant) & (self.population_energy > config.cost_mate)

        for d1, d2 in nearest_neighbours:
            if (d1, d2) not in seen_deer_pairs:
                # Check if they are valid mates
                # Check sex
                if self.population_sex[d1] == 0 and self.population_sex[d2] == 0: # If both female
                    seen_deer_pairs.add((d1, d2))
                    continue
                if self.population_sex[d1] == 1 and self.population_sex[d2] == 1: # If both male
                    seen_deer_pairs.add((d1, d2))
                    continue

                if self.population_sex[d1] == 0:
                    male = d2
                    female = d1
                else:
                    male = d1
                    female = d2

                # Check if mateable and add gestation period counter to pregnant female
                if self.population_mateable[male] and self.population_mateable[female]:
                    self.population_mateable[female] = False
                    self.population_isPregnant[female] = True

                    # Initialize pregnancy inside female
                    # Randomly select alleles
                    allele1 = np.random.choice(self.population_germ_genotype[female])
                    allele2 = np.random.choice(self.population_germ_genotype[male])
                    self.population_embryo_dict[female] = [config.gestation_period, allele1, allele2]
    
    def deer_spawn(self):
        # Spawn deer whos gestation period has reached value of 1
        # Subtract value; level minimum to zero

        # Subtract gestation timers from all deers
        self.population_embryo_dict[:, 0] -= 1

        # Dont let timers go below zero
        self.population_embryo_dict[:, 0] = np.clip(self.population_embryo_dict[:, 0],0, None )

        # Mask of those pregnant deers who are ready to give birth
        newbirth_mask = self.population_embryo_dict[:, 0] == 1

        # Number of progeny being born
        count_births = sum(newbirth_mask)

        # Reset pregnancy and mateable status of mother
        self.population_isPregnant[newbirth_mask] = False

        # Give birth at position of female deer
        positions = self.population_coords[newbirth_mask]
        self.population_coords = np.concatenate((self.population_coords, positions))
        self.population_energy = np.concatenate((self.population_energy, np.full(shape=(count_births), fill_value=config.initial_energy)))
        self.population_age = np.concatenate((self.population_age, np.zeros(shape=count_births)))
        self.population_genotype = np.concatenate((self.population_genotype, self.population_embryo_dict[newbirth_mask][:,1:]))
        self.population_germ_genotype = np.copy(self.population_genotype)
        self.population_isPregnant = np.concatenate((self.population_isPregnant, np.full(shape=count_births, fill_value=False)))
        self.population_mateable = np.concatenate((self.population_mateable, np.full(shape=count_births, fill_value=False)))
        self.population_sex = np.concatenate((self.population_sex, np.random.choice( [0, 1], count_births)))
        self.population_embryo_dict = np.concatenate((self.population_embryo_dict, np.zeros(shape=(count_births, 3))))

        
        self.population_mateable = (self.population_age >= config.maturity_age) & (~self.population_isPregnant) & (self.population_energy > config.cost_mate)

        # Re-calculate population size
        self.N = len(self.population_coords)
        
    def natural_select(self):

        # Select only for deer who have turned adults this tick
        birthday_deers = self.population_age == config.maturity_age
        immune_deer = self.population_age != config.maturity_age

        # Create masks for different genotypes
        AA_mask = (np.sum(self.population_genotype, axis=1) == 2) & (birthday_deers)
        Aa_mask = (np.sum(self.population_genotype, axis=1) == 1) & (birthday_deers)
        aa_mask = (np.sum(self.population_genotype, axis=1) == 0) & (birthday_deers)

        # Generate random uniform 0-1 arrays to filter survivors
        rand = np.random.uniform(size=len(self.population_genotype))

        # Create survivor masks for each group
        AA_survivor_mask = (rand <= config.fitness_AA) & (AA_mask)
        Aa_survivor_mask = (rand <= config.fitness_Aa) & (Aa_mask)
        aa_survivor_mask = (rand <= config.fitness_aa) & (aa_mask)

        # Create a master survivor mask; Add immune_deers to prevent population wipeout
        master_survivor_mask = AA_survivor_mask | Aa_survivor_mask | aa_survivor_mask | immune_deer

        # Update each array to inlcude only survivors
        self.population_energy = self.population_energy[master_survivor_mask]
        self.population_age = self.population_age[master_survivor_mask]
        self.population_coords = self.population_coords[master_survivor_mask]
        self.population_genotype = self.population_genotype[master_survivor_mask]
        self.population_germ_genotype = self.population_germ_genotype[master_survivor_mask]
        self.population_isPregnant = self.population_isPregnant[master_survivor_mask]
        self.population_mateable = self.population_mateable[master_survivor_mask]
        self.population_sex = self.population_sex[master_survivor_mask]
        self.population_embryo_dict = self.population_embryo_dict[master_survivor_mask]

        # Update population varaibles
        self.N = len(self.population_energy)
        


    def deer_die(self):
        
        # Select survivors/alive deer
        survivor_mask = (self.population_energy > 0) & (self.population_age < config.life_span) 

        # Update each array to inlcude only survivors
        self.population_energy = self.population_energy[survivor_mask]
        self.population_age = self.population_age[survivor_mask]
        self.population_coords = self.population_coords[survivor_mask]
        self.population_genotype = self.population_genotype[survivor_mask]
        self.population_germ_genotype = self.population_germ_genotype[survivor_mask]
        self.population_isPregnant = self.population_isPregnant[survivor_mask]
        self.population_mateable = self.population_mateable[survivor_mask]
        self.population_sex = self.population_sex[survivor_mask]
        self.population_embryo_dict = self.population_embryo_dict[survivor_mask]

        # Update population varaibles
        self.N = len(self.population_energy)


    def run_tick(self):
        if self.N > 0:
            print(f"| {self.tick:^9} | {self.N:^7} | {self.p:^7.3f} | {self.population_energy.mean():^11.1f} | {self.grass.mean():^9.1f} | {self.population_age.mean():^9.2f} |")
        else:
            print(f"| {self.tick:^9} | {self.N:^7} | {self.p:^7} | {0:^11.1f} | {self.grass.mean():^5.1f}")

        # Grow the grass
        self.grow_grass()

        # Nautrally select fit deers
        self.natural_select()

        # Move the deer + metabolic cost
        self.deer_move()

        # Deer eats grass
        self.deer_eat()

        # Deers breed
        self.deer_breed()

        # Deer Spawn
        self.deer_spawn()

        # Deer die
        self.deer_die()

        # Age the deer
        self.deer_age()

        # Recalculate parameters
        self.population_mateable = (self.population_age >= config.maturity_age) & (~self.population_isPregnant) & (self.population_energy > config.cost_mate)

        # Update p value based on germ genotype
        self.p = self.population_germ_genotype.mean()
        self.q = 1 - self.p
        
        # Update tick
        self.tick += 1
