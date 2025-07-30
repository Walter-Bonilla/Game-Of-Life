import numpy as np
from numba import njit, prange
import time
import matplotlib.pyplot as plt
from juego import GameOfLife

@njit
def count_neighbors_numba(board, x, y):
    """Versión optimizada con Numba para contar vecinos"""
    rows, cols = board.shape
    neighbors = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            nx, ny = (x + i) % rows, (y + j) % cols
            neighbors += board[nx, ny]
    return neighbors

@njit(parallel=True)
def step_numba(board):
    """Paso del Juego de la Vida paralelizado con Numba"""
    new_board = np.zeros_like(board)
    rows, cols = board.shape
    
    # Paralelización automática con prange
    for i in prange(rows):
        for j in range(cols):
            neighbors = count_neighbors_numba(board, i, j)
            
            # Reglas del Juego de la Vida
            if board[i, j] == 1:  # Celda viva
                if neighbors < 2 or neighbors > 3:
                    new_board[i, j] = 0
                else:
                    new_board[i, j] = 1
            else:  # Celda muerta
                if neighbors == 3:
                    new_board[i, j] = 1
    
    return new_board

class GameOfLifeParallel:
    def __init__(self, rows, cols, initial_state=None):
        self.rows = rows
        self.cols = cols
        self.board = initial_state if initial_state is not None else np.random.choice([0, 1], size=(rows, cols))
    
    def run(self, steps):
        """Ejecuta la simulación para un número dado de pasos"""
        for _ in range(steps):
            self.board = step_numba(self.board)
    
    def animate(self, frames, interval=200):
        """Crea una animación (requiere matplotlib)"""
        fig, ax = plt.subplots()
        img = ax.imshow(self.board, cmap='binary')
        plt.title("Juego de la Vida Paralelo")
        
        def update(frame):
            self.board = step_numba(self.board)
            img.set_array(self.board)
            return [img]
        
        from matplotlib.animation import FuncAnimation
        ani = FuncAnimation(fig, update, frames=frames, interval=interval, blit=True)
        plt.close()
        return ani

# Función para análisis de rendimiento
def performance_test():
    sizes = [64, 128, 256, 512, 1024]
    times_serial = []
    times_parallel = []
    
    for size in sizes:
        print(f"Probando tamaño {size}x{size}...")
        
        # Versión serial (original)
        game_serial = GameOfLife(size, size)
        start = time.time()
        game_serial.run(10)
        times_serial.append((time.time() - start)/10)
        
        # Versión paralela con Numba
        game_parallel = GameOfLifeParallel(size, size, game_serial.board.copy())
        start = time.time()
        game_parallel.run(10)
        times_parallel.append((time.time() - start)/10)
    
    # Graficar resultados
    plt.figure(figsize=(10, 5))
    plt.plot(sizes, times_serial, 'o-', label='Serial')
    plt.plot(sizes, times_parallel, 'o-', label='Paralelo (Numba)')
    plt.xlabel('Tamaño del tablero')
    plt.ylabel('Tiempo por iteración (s)')
    plt.title('Comparación de rendimiento Serial vs. Paralelo')
    plt.legend()
    plt.grid(True)
    plt.savefig('performance_comparison.png')
    plt.show()
    
    return sizes, times_serial, times_parallel

if __name__ == "__main__":
    print("=== Juego de la Vida Paralelo con Numba ===")
    print("Ejecutando prueba de rendimiento...")
    sizes, t_serial, t_parallel = performance_test()
    
    print("\nResultados:")
    for size, ts, tp in zip(sizes, t_serial, t_parallel):
        speedup = ts / tp
        print(f"Tamaño {size}x{size}:")
        print(f"  Serial: {ts:.4f}s | Paralelo: {tp:.4f}s | Speedup: {speedup:.2f}x")