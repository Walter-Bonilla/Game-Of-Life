# Libreria
from mpi4py import MPI  
import numpy as np  
import sys

# Inicializamos el comunicador MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()  # Identificador único de cada proceso
size = comm.Get_size()  # Número total de procesos

# Proceso raíz (rank 0) es el que coordina todo
if rank == 0:
    # Verificamos que se haya pasado el tamaño del arreglo como argumento
    if len(sys.argv) != 2:
        print("Uso: mpirun -np 4 python estadisticas_mpi.py <tamaño_del_arreglo>")
        sys.exit(1)
    
    # Obtenemos el tamaño del arreglo del argumento
    N = int(sys.argv[1])
    
    # Verificamos que N sea divisible entre el número de procesos
    if N % size != 0:
        print(f"El tamaño del arreglo ({N}) debe ser divisible entre el número de procesos ({size})")
        sys.exit(1)
    
    # Creamos un arreglo de N números aleatorios entre 0 y 100
    arreglo_completo = np.random.uniform(0, 100, N)
else:
    # Los otros procesos no tienen el arreglo inicialmente
    arreglo_completo = None
    N = None

# Etapa 1: Distribuir el tamaño del arreglo a todos los procesos
# Usamos MPI_Bcast para enviar el valor de N desde el proceso 0 a todos
N = comm.bcast(N, root=0)

# Calculamos cuántos elementos le tocan a cada proceso
elementos_por_proceso = N // size

# Etapa 2: Dividir el arreglo y enviar partes a cada proceso
# Creamos un arreglo local en cada proceso para recibir su parte
arreglo_local = np.empty(elementos_por_proceso, dtype=np.float64)

# Usamos Scatter para repartir el arreglo grande en partes iguales
comm.Scatter(arreglo_completo, arreglo_local, root=0)

# Etapa 3: Cada proceso calcula sus estadísticas locales
minimo_local = np.min(arreglo_local)
maximo_local = np.max(arreglo_local)
suma_local = np.sum(arreglo_local)
# El promedio local no es necesario para el promedio global, pero lo calculamos por si acaso
promedio_local = suma_local / elementos_por_proceso

# Etapa 4: Calcular estadísticas globales usando Reduce
# Para el mínimo global: comparamos todos los mínimos locales y nos quedamos con el más pequeño
minimo_global = comm.reduce(minimo_local, op=MPI.MIN, root=0)

# Para el máximo global: comparamos todos los máximos locales y nos quedamos con el más grande
maximo_global = comm.reduce(maximo_local, op=MPI.MAX, root=0)

# Para el promedio global: sumamos todas las sumas locales y dividimos entre N
suma_global = comm.reduce(suma_local, op=MPI.SUM, root=0)
# Solo el proceso 0 necesita calcular el promedio global
if rank == 0:
    promedio_global = suma_global / N

# Opcional: Reconstruir el arreglo completo en el proceso raíz usando Gather
if rank == 0:
    arreglo_reconstruido = np.empty(N, dtype=np.float64)
else:
    arreglo_reconstruido = None

comm.Gather(arreglo_local, arreglo_reconstruido, root=0)

# Etapa 5: El proceso raíz imprime los resultados
if rank == 0:
    print("\n--- Resultados Estadísticos ---")
    print(f"Tamaño del arreglo: {N}")
    print(f"Número de procesos: {size}")
    print(f"Elementos por proceso: {elementos_por_proceso}")
    print(f"Mínimo global: {minimo_global:.4f}")
    print(f"Máximo global: {maximo_global:.4f}")
    print(f"Promedio global: {promedio_global:.4f}")
    
    # Verificación opcional (solo para debugging)
    print("\nVerificación (usando numpy directamente en el arreglo completo):")
    print(f"Mínimo numpy: {np.min(arreglo_completo):.4f}")
    print(f"Máximo numpy: {np.max(arreglo_completo):.4f}")
    print(f"Promedio numpy: {np.mean(arreglo_completo):.4f}")
    
    # Verificación de que el arreglo se reconstruyó correctamente (opcional)
    if np.allclose(arreglo_completo, arreglo_reconstruido):
        print("\nEl arreglo se reconstruyó correctamente con Gather")
    else:
        print("\n¡Error en la reconstrucción del arreglo!")