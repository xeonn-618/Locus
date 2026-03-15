# Define the parameters of the simulation in this file

# Deer Population Variables
initial_population_size = 100
initial_energy = 100
maturity_age = 5 # Age when deer achieves reproductive maturity
cost_move = 5
cost_metabolic = 2


# -> Genetic Variables
initial_p = 0.7 # Allelic frequency of dominant allele

# Environment Variables

# Note: Certain combinations of grass_growth_max, sigma and matrix_size may break the simulation at start.
# This will appear as no grass in the environment/ avg food being zero. This will happen because the gaussion filter being normalized
# over a very small range (usually grass_growth_max <= 5) results in a flat map of zeros. 
# To avoid this, choose smaller sigmas and bigger grass growth max, if needed increase grid size.

matrix_size = 500 # size of environment
sigma = 14 # smoothness of grass distribution; larger = smoother patches; small = finer patches
grass_growth_max = 10
grass_max_length = 2000

# Animation Variables
tick_time = 50 # Time per tick in miliseconds