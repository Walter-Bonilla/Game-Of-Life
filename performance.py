import cProfile
import pstats
import numpy as np
from juego import GameOfLife
from line_profiler import LineProfiler
import matplotlib.pyplot as plt
import os

# Parte 1: Análisis con cProfile
def profile_game_of_life():
    """Ejecuta el Juego de la Vida con cProfile y guarda los resultados."""
    # Configuración de la simulación
    rows, cols = 512, 512
    steps = 100
    
    # Crear instancia del juego
    game = GameOfLife(rows, cols, create_random(rows, cols, density=0.2))
    
    # Configurar cProfile
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Ejecutar simulación
    game.run(steps)
    
    profiler.disable()
    
    # Guardar resultados en archivo
    if not os.path.exists('profiling_results'):
        os.makedirs('profiling_results')
    
    # Guardar estadísticas en texto
    with open('profiling_results/cprofile_stats.txt', 'w') as f:
        stats = pstats.Stats(profiler, stream=f)
        stats.sort_stats('cumulative')
        stats.print_stats()
    
    # Guardar para visualización con snakeviz
    stats.dump_stats('profiling_results/cprofile_stats.pstats')
    
    print("Resultados de cProfile guardados en profiling_results/")
    print("Para visualizar con snakeviz: snakeviz profiling_results/cprofile_stats.pstats")

# Parte 2: Análisis con line_profiler
def line_profile_game_of_life():
    """Analiza línea por línea las funciones críticas del Juego de la Vida."""
    # Configuración de la simulación
    rows, cols = 128, 128  # Más pequeño para line_profiler
    steps = 10
    
    # Crear instancia del juego
    game = GameOfLife(rows, cols, create_random(rows, cols, density=0.2))
    
    # Configurar line_profiler
    lp = LineProfiler()
    
    # Registrar las funciones a analizar
    lp.add_function(GameOfLife.step)
    lp.add_function(GameOfLife.count_neighbors)
    
    # Ejecutar con profiling
    lp_wrapper = lp(game.run)
    lp_wrapper(steps)
    
    # Guardar resultados
    if not os.path.exists('profiling_results'):
        os.makedirs('profiling_results')
    
    with open('profiling_results/line_profiler_stats.txt', 'w') as f:
        lp.print_stats(output_unit=1e-3, stream=f)  # Mostrar tiempos en milisegundos
    
    print("Resultados de line_profiler guardados en profiling_results/line_profiler_stats.txt")

# Funciones auxiliares (copiadas del código original para completitud)
def create_random(rows: int, cols: int, density: float = 0.2) -> np.ndarray:
    """Crea un tablero con celdas aleatorias."""
    return np.random.choice([0, 1], size=(rows, cols), p=[1-density, density])

# Parte 3: Visualización de resultados
def plot_performance():
    """Genera gráficos de rendimiento basados en los datos recolectados."""
    # Ejemplo: Tiempo por tamaño de tablero
    sizes = [64, 128, 256, 512, 1024]
    times = [0.1, 0.4, 1.6, 6.4, 25.6]  # Valores de ejemplo - deberías reemplazarlos con datos reales
    
    plt.figure(figsize=(10, 5))
    plt.plot(sizes, times, 'o-')
    plt.xlabel('Tamaño del tablero (n×n)')
    plt.ylabel('Tiempo por iteración (ms)')
    plt.title('Escalabilidad del Juego de la Vida')
    plt.grid(True)
    plt.savefig('profiling_results/performance_scaling.png')
    plt.close()
    
    print("Gráfico de rendimiento guardado en profiling_results/performance_scaling.png")

if __name__ == "__main__":
    print("=== Análisis de rendimiento del Juego de la Vida ===")
    print("\nParte 1: Ejecutando cProfile...")
    profile_game_of_life()
    
    print("\nParte 2: Ejecutando line_profiler...")
    line_profile_game_of_life()
    
    print("\nParte 3: Generando gráficos de rendimiento...")
    plot_performance()
    
    print("\nAnálisis completado. Revise los archivos en el directorio profiling_results/")