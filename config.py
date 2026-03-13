# Define the parameters of the simulation in this file

# Deer Population Variables
initial_population_size = 100
initial_energy = 100
maturity_age = 5 # Age when deer achieves reproductive maturity

# -> Genetic Variables
initial_p = 0.7 # Allelic frequency of dominant allele

# Environment Variables
matrix_size = 500 # size of environment
sigma = 20 # smoothness of grass distribution; larger = smoother patches; small = finer patches
grass_growth_max = 6
grass_max_length = 150

# Animation Variables
tick_time = 500 # Time per tick in miliseconds