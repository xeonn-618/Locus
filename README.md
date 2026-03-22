# Locus - A Genetics Simulation

> A highly customizable, dynamic Python-based spatial genetic engine (1 locus, 2 alleles) that simulates a deer population evolving over time.

## 🧬 Overview
This simulation was built as a submission for a creative expression project. It aims to be accessible to students who are learning population genetics, acting as a sandbox tool to tweak initial parameters and watch how the population evolves (or doesn't!).

## ✨ Features
* **Full Customization:** A dedicated `config.py` file grants full control over the ecosystem's parameters and starting conditions.
* **Real-Time Dashboard:** A live Matplotlib animation displaying the spatial deer map, tracking allelic frequencies, and graphing genotype population dynamics.
* **High-Performance Computation:** Utilizes NumPy vectorization for fast, O(1) array operations, avoiding slow Python loops.
* **Spatial Hashing:** Implements a C-optimized `KDTree` data structure via SciPy for highly efficient nearest-neighbor mating queries.
* **Dynamic Environment:** Features a randomized, smooth grass-growing simulation that acts as the primary food source.
* **Emergent Carrying Capacity:** The environment's carrying capacity is not hardcoded; it is a direct product of the rule-based deer metabolism and grass regeneration simulation.

## 🏗️ Architecture
The simulation engine is decoupled into four core Python files for maintainability and performance:

* `main.py`: Initializes the simulation with the configuration parameters and launches the animation loop.
* `simulator.py`: The core physics and biology engine. It defines the `Simulator` class, manages the vectorized deer arrays, and handles the logic for metabolism, spatial movement, breeding, and natural selection.
* `animate.py`: The frontend rendering engine. Contains the Matplotlib-based functions and HUD logic to take the simulation state and animate it smoothly onto a figure.
* `config.py`: The control panel containing the global variables and tweakable parameters for the ecosystem.

## 🚀 Installation & Setup
To run this simulation locally, you will need Python 3.x installed. 

1. **Clone the repository:**
   ```bash
   git clone https://github.com/xeonn-618/Locus.git
   cd Locus
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the simulation:**
   ```bash
   python main.py
   ```

---

## ⚙️ Usage & Parameters

All simulation parameters are set in `config.py`. Edit the values there to change the state and results of the simulation.

### 🦌 Deer Population

| Parameter | Default | Description |
|---|---|---|
| `life_span` | `10*year` | An arbitrary conversion for ticks to years |
| `initial_population_size` | `250` | Initial Population Size (1:1 Sex Ratio) |
| `initial_energy` | `400` | Initial energy of each individual or newborns|
| `vision_radius` | `2` | Defines how far a deer can move with it being in the center in search for grass. Ex. 1:3x3, 2:5x5 etc|
| `mating_dist` | `5` | Euclidean distance required for two deers to mate. |
| `maturity_age` | `5*year` | Age when deers reach adulthood and attain reproductive maturity |
| `max_eat` | `250` | Maximum length a deer can eat per tick |
| `digestion_efficency` | `0.5` | Fraction of consumed grass length that gets converted into energy |
| `cost_move` | `25` | Energy cost required to move 1 unit|
| `cost_metabolic` | `10` | Energy cost required to sustain life every tick |
| `cost_mate` | `100` | Energy cost required for two deers to mate |
| `exploration_rate` | `0.1` | Change factor of how often deers randomly wander per tick |
| `gestation_period` | `0.7*year` | Ticks required to go from pregnancy to childbirth. Must be an integer |

### 🧬 Genetics

| Parameter | Default | Description |
|---|---|---|
| `initial_p` | `0.5` | Initial allelic frequency of dominant allele A|
| `fitness_AA` | `0.90` | Fitness of AA genotype individual |
| `fitness_Aa` | `0.90` | Fitness of Aa type individual |
| `fitness_aa` | `0.50` | Fitness of aa type individual|

### 🌿 Environment

| Parameter | Default | Description |
|---|---|---|
| `matrix_size` | `100` | Defines the side of the sqaure environment matrix |
| `sigma` | `2` | Standard deviation of gaussian kernel. Controls blurring amount of grass patches. Bigger sigma gives larger patches |
| `grass_growth_max` | `10` | Max length growth of grass per tick |
| `grass_max_length` | `2000` | Max length grass can attain |

### 🎬 Animation

| Parameter | Default | Description |
|---|---|---|
| `tick_time` | `25` | Time in miliseconds for each tick |