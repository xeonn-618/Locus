import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import config

def run(sim):

    # Create fig, ax objects
    fig, ax = plt.subplots(figsize=(6,6))

    # Create a grass heatmap
    grass_map = ax.imshow(sim.grass, cmap='Greens', interpolation='nearest', alpha=0.5)

    # Create a population scatter map
    population_map = ax.scatter(sim.population_coords[:, 0], sim.population_coords[:, 1], alpha=1, marker='d')

    # Set plot title and legend
    ax.set_title('Grass Simulation')
    # ax.legend(loc='upper right')

    # Create text to show information
    text = ax.text(
        0.03, 0.97, f'Tick: {sim.tick}\nAvg Food: {np.mean(sim.grass)}\nN: {sim.N}',
        transform=ax.transAxes, # Relative to axes
        fontsize=10,
        verticalalignment='top',
        fontfamily='monospace'
    )

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

        # Return the axes objects
        return [grass_map, text, population_map]

    # Create the animation object
    ani = animation.FuncAnimation(fig,
                                  update,
                                  interval=config.tick_time,
                                  blit=True,
                                  cache_frame_data=False
                                  )
    
    # Run the animation
    plt.show()