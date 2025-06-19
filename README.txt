# Juego de la Vida de Conway

Implementación del autómata celular "Juego de la Vida" propuesto por John Conway.

## Requisitos

- Python 3.6+
- NumPy
- Matplotlib

Instalar dependencias:
pip install numpy matplotlib

## Uso básico

1. Crear una instancia del juego:
```python
from game_of_life import GameOfLife, create_glider

# Tablero 20x20 con un planeador
game = GameOfLife(20, 20, create_glider(20, 20))

2.Ejecutar pasos:

game.step()  # Un paso
game.run(10)  # 10 pasos

Visualizar:

# Animación de 50 generaciones
ani = game.animate(frames=50)
plt.show()

Patrones incluidos

create_glider(rows, cols): Crea un planeador

create_blinker(rows, cols): Crea un parpadeador

create_random(rows, cols, density=0.2): Crea un tablero aleatorio


Pruebas de rendimiento
Ejecutar:

python
from game_of_life import performance_test, plot_performance

sizes, times = performance_test(max_power=8)  # Hasta 256x256
plot_performance(sizes, times)


Análisis de rendimiento
La implementación actual tiene una complejidad O(n²) donde n es el número de celdas, ya que cada paso requiere visitar todas las celdas del tablero. Las gráficas log-log permiten visualizar esta relación.
