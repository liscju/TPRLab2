mpicc -o main.out main.c -lrt
mpiexec -n 3 ./main.out -f ../gandalf-mpihosts
mpiexec -n 5 ./main.out -f ../gandalf-mpihosts
mpiexec -n 10 ./main.out -f ../gandalf-mpihosts
