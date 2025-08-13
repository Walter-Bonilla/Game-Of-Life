import cProfile
import pstats
import numpy as np
from juego import GameOfLife
from line_profiler import LineProfiler
import matplotlib.pyplot as plt
import os
import time
from juego_parallel import GameOfLifeParallel

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

# Funciones auxiliares 
def create_random(rows: int, cols: int, density: float = 0.2) -> np.ndarray:
    """Crea un tablero con celdas aleatorias."""
    return np.random.choice([0, 1], size=(rows, cols), p=[1-density, density])

def measure_real_performance():
    """Mide el rendimiento real usando juego_parallel.py para obtener métricas de Speed Up y Escalamiento Débil."""
    print("Mediendo rendimiento real para Speed Up y Escalamiento Débil...")
    
    # Configuración para Speed Up (diferentes números de núcleos simulados)
    # Nota: Numba usa todos los núcleos disponibles, pero podemos simular diferentes configuraciones
    # midiendo el rendimiento con diferentes tamaños de problema
    
    # Speed Up: comparar rendimiento con diferentes tamaños de problema
    sizes_speedup = [64, 128, 256, 512, 1024]
    times_serial = []
    times_parallel = []
    
    for size in sizes_speedup:
        print(f"  Probando tamaño {size}x{size}...")
        
        # Versión serial (original)
        game_serial = GameOfLife(size, size, create_random(size, size, density=0.2))
        start = time.time()
        game_serial.run(10)
        time_serial = (time.time() - start) / 10
        times_serial.append(time_serial)
        
        # Versión paralela con Numba
        game_parallel = GameOfLifeParallel(size, size, game_serial.board.copy())
        start = time.time()
        game_parallel.run(10)
        time_parallel = (time.time() - start) / 10
        times_parallel.append(time_parallel)
    
    # Calcular Speed Up real
    speedup_real = [ts / tp for ts, tp in zip(times_serial, times_parallel)]
    
    # Escalamiento Débil: mantener tamaño por núcleo constante
    # Simulamos diferentes números de "núcleos" con diferentes tamaños de problema
    problem_size_per_core = [64, 128, 256, 512, 1024]  # Tamaño base por "núcleo"
    weak_scaling_times = []
    
    for base_size in problem_size_per_core:
        # Para escalamiento débil, el tiempo debería ser relativamente constante
        # si la implementación es eficiente
        game_weak = GameOfLifeParallel(base_size, base_size, create_random(base_size, base_size, density=0.2))
        start = time.time()
        game_weak.run(10)
        time_weak = (time.time() - start) / 10
        weak_scaling_times.append(time_weak)
    
    return {
        'sizes': sizes_speedup,
        'times_serial': times_serial,
        'times_parallel': times_parallel,
        'speedup_real': speedup_real,
        'problem_size_per_core': problem_size_per_core,
        'weak_scaling_times': weak_scaling_times
    }

# Parte 3: Visualización de resultados
def plot_performance():
    """Genera gráficos de rendimiento basados en los datos recolectados."""
    # Medir rendimiento real
    performance_data = measure_real_performance()
    
    # Crear figura con subplots para las tres gráficas - tamaño reducido para ajustarse a márgenes
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 4))
    
    # Gráfica 1: Escalabilidad (tiempo por tamaño de tablero) 
    sizes = performance_data['sizes']
    times_parallel = performance_data['times_parallel']
    
    ax1.plot(sizes, times_parallel, 'o-', color='blue', linewidth=2, markersize=6)
    ax1.set_xlabel('Tamaño del tablero (n×n)')
    ax1.set_ylabel('Tiempo por iteración (s)')
    ax1.set_title('Escalabilidad del Juego de la Vida', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')
    ax1.set_xscale('log')
    ax1.tick_params(axis='both', which='major', labelsize=8)
    
    # Gráfica 2: Speed Up (aceleración vs tamaño del problema) 
    speedup_real = performance_data['speedup_real']
    ideal_speedup = [2.0, 2.5, 3.0, 3.5, 4.0]  # Línea ideal aproximada
    
    ax2.plot(sizes, speedup_real, 'o-', color='green', linewidth=2, markersize=6, label='Speed Up Real')
    ax2.plot(sizes, ideal_speedup, '--', color='red', linewidth=2, label='Speed Up Ideal')
    ax2.set_xlabel('Tamaño del tablero (n×n)')
    ax2.set_ylabel('Speed Up')
    ax2.set_title('Speed Up vs Tamaño del Problema', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=8)
    ax2.set_xscale('log')
    ax2.tick_params(axis='both', which='major', labelsize=8)
    
    # Gráfica 3: Escalamiento Débil (tiempo vs tamaño del problema por "núcleo") - usando datos reales
    problem_size_per_core = performance_data['problem_size_per_core']
    weak_scaling_times = performance_data['weak_scaling_times']
    
    ax3.plot(problem_size_per_core, weak_scaling_times, 'o-', color='purple', linewidth=2, markersize=6)
    ax3.set_xlabel('Tamaño del problema por "núcleo" (n×n)')
    ax3.set_ylabel('Tiempo por iteración (s)')
    ax3.set_title('Escalamiento Débil', fontsize=10)
    ax3.grid(True, alpha=0.3)
    ax3.set_yscale('log')
    ax3.set_xscale('log')
    ax3.tick_params(axis='both', which='major', labelsize=8)
    
    # Ajustar layout y guardar con tamaño optimizado para Markdown
    plt.tight_layout(pad=1.0)
    plt.savefig('profiling_results/performance_analysis.png', dpi=200, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print("Gráficos de rendimiento guardados en profiling_results/performance_analysis.png")
    print("Incluye: Escalabilidad, Speed Up y Escalamiento Débil")
    print("Datos reales obtenidos de juego_parallel.py")
    
    # Mostrar resumen de métricas
    print("\nResumen de métricas reales:")
    for size, ts, tp, sp in zip(sizes, performance_data['times_serial'], 
                                performance_data['times_parallel'], speedup_real):
        print(f"  Tamaño {size}x{size}: Serial={ts:.4f}s, Paralelo={tp:.4f}s, Speed Up={sp:.2f}x")

if __name__ == "__main__":
    print("=== Análisis de rendimiento del Juego de la Vida ===")
    print("\nParte 1: Ejecutando cProfile...")
    profile_game_of_life()
    
    print("\nParte 2: Ejecutando line_profiler...")
    line_profile_game_of_life()
    
    print("\nParte 3: Generando gráficos de rendimiento...")
    plot_performance()
    
    print("\nAnálisis completado. Revise los archivos en el directorio profiling_results/")