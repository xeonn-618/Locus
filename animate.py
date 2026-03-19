import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Patch
import mplcyberpunk
import numpy as np
import config

plt.style.use('cyberpunk')

def run(sim):

    # define the grid layout
    layout = [
        ['map', 'freq'],
        ['map', 'pop']
    ]

    # Create fig, ax objects
    fig, ax = plt.subplot_mosaic(layout, figsize=(12, 6), width_ratios=(1,1)) #type: ignore

    # Setup map object
    # Create a grass heatmap
    grass_map = ax['map'].imshow(sim.grass, cmap='Greens', interpolation='nearest', alpha=0.25)

    # Retrieve genotypes of individuals
    genotype_sums = np.sum(sim.population_genotype, axis=1)

    # Create a color palette for the different genotypes
    # aa = red; Aa = Purple; AA = Blue
    palette = np.array(['#ff007f', '#b200ff', '#00ffff'])

    # Assign deer indicies colors
    deer_colors = palette[genotype_sums]

    # Create a population scatter map
    population_map = ax['map'].scatter(sim.population_coords[:, 0], sim.population_coords[:, 1], alpha=1, marker='o',
                                       c=deer_colors, edgecolors='black', linewidth=0.8, s=55)

    # Set plot title and legend
    ax['map'].set_title('Grass & Deer Simulation')
    AA_patch = Patch(color=palette[2], label='AA')
    Aa_patch = Patch(color=palette[1], label='Aa')
    aa_patch = Patch(color=palette[0], label='aa')
    ax['map'].legend(handles=[AA_patch, Aa_patch, aa_patch], loc='upper right')


    # Create text to show information
    text = ax['map'].text(
        0.03, 0.97, f'Tick: {sim.tick}\nAvg Food: {np.mean(sim.grass)}\nN: {sim.N}',
        transform=ax['map'].transAxes, # Relative to axes
        fontsize=10,
        verticalalignment='top',
        fontfamily='monospace'
    )

    # Setup frequency plot object
    ax['freq'].set_title('Allelic Frequencies')
    ax['freq'].set_ylim(0,1)
    line_p, = ax['freq'].plot([], [], label='p (Dominant)', color='blue', lw=2)
    line_q, = ax['freq'].plot([], [], label='q (Recessive))', color='red', lw=2)
    ax['freq'].legend(loc='upper left')

    # Setup population density plot
    ax['pop'].set_title('Population Density (N)')
    line_N, = ax['pop'].plot([], [], color='green', lw=2)

    fig.tight_layout() 

    # Data Storage
    history_ticks = []
    history_p = []
    history_q = []
    history_N = []

    # Update the tick
    def update(frame):

        # Run simulation tick
        sim.run_tick()

        # Update the text
        status_text = f"Tick: {sim.tick}\nAvg Food: {np.mean(sim.grass)}\nN: {sim.N}"
        text.set_text(status_text)

        # Update grass heatmap
        grass_map.set_data(sim.grass)

        # Update limits of heatmap as grass range changes
        grass_map.set_clim(vmin=np.min(sim.grass), vmax=np.max(sim.grass))

        # Update population map
        population_map.set_offsets(sim.population_coords)

        # Update deer colors
        genotype_sums = np.sum(sim.population_genotype, axis=1).astype(int)
        new_deer_colors = palette[genotype_sums]
        population_map.set_facecolors(new_deer_colors)

        # Calculate current sim stats
        present_N = len(sim.population_coords)

        # If all die, prevent div by zero
        if present_N > 0:
            total_alleles = 2 * present_N
            current_p = sim.population_genotype.sum() / total_alleles
            current_q = 1 - current_p
        else:
            current_p = 0
            current_q = 0

        # Update history lists
        history_N.append(present_N)
        history_p.append(current_p)
        history_q.append(current_q)
        history_ticks.append(sim.tick)

        # Update line plots
        line_N.set_data(history_ticks, history_N)
        line_p.set_data(history_ticks, history_p)
        line_q.set_data(history_ticks, history_q)

        # Slide the axis
        window_start = max(0, sim.tick - 100)
        window_end = max(10, sim.tick + 5)
        ax['freq'].set_xlim(window_start, window_end)
        ax['pop'].set_xlim(window_start, window_end)

        # Scale population Y axis
        if present_N > 0:
            ax['pop'].set_ylim(0, max(history_N) + 10)

        # Return the axes objects
        return [grass_map, text, population_map, line_N, line_p, line_q]

    # Create the animation object
    ani = animation.FuncAnimation(fig,
                                  update,
                                  interval=config.tick_time,
                                  blit=False,
                                  cache_frame_data=False
                                  )
    
    # Run the animation
    plt.show()