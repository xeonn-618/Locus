# Define the parameters of the simulation in this file

# Deer Population Variables
initial_population_size = 250 # Initial population size of simulation
initial_energy = 400 # Initial energy of each deer at start of simulation
vision_radius = 2 # how far deer an interact; 1 for 3x3 grid with deer at center, 2 for 5x5 " " "
mating_dist = 5 # eucledian-distance required for two deers to breed
maturity_age = 50 # Age in ticks when deer achieves reproductive maturity
max_eat = 250 # max length of grass a deer can consume per tick
digestion_efficency = 0.5 # Multiplication factor of how much of grass length is converted into energy
cost_move = 25 # Energy required to move 1 step
cost_metabolic = 10 # Energy consumed by metabolic processes each step
cost_mate = 100 # Breeding energy cost
exploration_rate = 0.1 # Probability a deer ignores optimal path and wanders randomly. Avoids crowding.
gestation_period = 50 # Gestation period of pregnancy in ticks

# -> Genetic Variables
initial_p = 0.8 # Allelic frequency of dominant allele

# Environment Variables

# Note: Certain combinations of grass_growth_max, sigma and matrix_size may break the simulation at start.
# This will appear as no grass in the environment/ avg food being zero. This will happen because the gaussion filter being normalized
# over a very small range (usually grass_growth_max <= 5) results in a flat map of zeros. 
# To avoid this, choose smaller sigmas and bigger grass growth max, if needed increase grid size.

matrix_size = 100 # size of environment
sigma = 2 # smoothness of grass distribution; larger = smoother patches; small = finer patches
grass_growth_max = 10
grass_max_length = 2000

# Animation Variables
tick_time = 25 # Time per tick in miliseconds