Requisitos y librerias necesarias

mpi4py
    >MPI (from mpi4py import MPI)
numpy
sys
time

Pasos para ejecutar el archivo llamado estadisticas_mpi.py

-Ejecuta en la terminal: mpiexec -np 4 python estadisticas_mpi.py 1000000

-Donde 4 es el número de procesos que quieres usar
Y 1000000 es el tamaño del arreglo (debe ser divisible entre 4)


*************************************************************************
* - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - *
*************************************************************************


Para ejecutar el archivo llamado latencia_p2p_mpi.py

mpiexec -np 2 python latencia_p2p_mpi.py

Donde 2 es el numero de procesos. 