mpicc -o main.out main.c -lrt
mpiexec -n 3 ./main.out
mpiexec -n 5 ./main.out
mpiexec -n 10 ./main.out
