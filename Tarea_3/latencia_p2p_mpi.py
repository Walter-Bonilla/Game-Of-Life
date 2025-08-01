from mpi4py import MPI
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def medir_latencia(N=10000, tamano_mensaje=1):
    if size != 2:
        if rank == 0:
            print("Error: Este programa requiere exactamente 2 procesos.")
        return

    # Proceso 0 envía y recibe; Proceso 1 recibe y envía
    mensaje = bytearray(tamano_mensaje)  # Mensaje de 1 byte (por defecto)
    tiempos = []

    if rank == 0:
        # Calentamiento (para evitar sesgos en la primera medición)
        comm.send(mensaje, dest=1)
        comm.recv(source=1)

        # Medición principal
        inicio_total = time.time()
        for _ in range(N):
            inicio = time.time()
            comm.send(mensaje, dest=1)
            comm.recv(source=1)
            fin = time.time()
            tiempos.append(fin - inicio)
        
        fin_total = time.time()
        
        # Cálculos estadísticos
        latencia_promedio = (fin_total - inicio_total) / N * 1e6  # Microsegundos
        latencia_unidireccional = latencia_promedio / 2

        print(f"\nMensaje de {tamano_mensaje} byte transmitido {N} veces.")
        print(f"Latencia promedio por mensaje (ida y vuelta): {latencia_promedio:.2f} microsegundos")
        print(f"Latencia estimada unidireccional: {latencia_unidireccional:.2f} microsegundos")

    elif rank == 1:
        for _ in range(N + 1):  # +1 por el calentamiento
            comm.recv(source=0)
            comm.send(mensaje, dest=0)

if __name__ == "__main__":
    medir_latencia(N=10000, tamano_mensaje=1)