import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
from typing import Optional, List, Tuple
from juego import GameOfLife, create_glider, create_blinker, create_random

def run_interactive_simulation():
    """Ejecuta una simulación interactiva con visualización"""
    print("=== JUEGO DE LA VIDA ===")
    print("Configuración inicial:")
    print("1. Planeador (Glider)")
    print("2. Parpadeador (Blinker)")
    print("3. Aleatorio")
    
    choice = input("Seleccione patrón inicial (1-3): ")
    rows, cols = 100, 100  # Tamaño por defecto
    
    if choice == "1":
        initial_state = create_glider(rows, cols)
    elif choice == "2":
        initial_state = create_blinker(rows, cols)
    else:
        density = float(input("Densidad (0.1-0.9): "))
        initial_state = create_random(rows, cols, density)
    
    game = GameOfLife(rows, cols, initial_state)
    frames = int(input("Número de generaciones a simular: "))
    
    print("\nIniciando animación... (Cierre la ventana para terminar)")
    ani = game.animate(frames=frames)
    plt.show()

if __name__ == "__main__":
    run_interactive_simulation()