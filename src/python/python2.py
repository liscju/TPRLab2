__author__ = 'bkumor'
from mpi4py import MPI
import socket
import sys

SEND_RECV_ITERATIONS = 100
BUFFER_SIZES = [1000, 5000, 10000,20000,30000,50000,100000,
              200000,300000,500000,1000000,2000000,3000000,
              5000000,6000000,10000000]

AVG_DELAY_TIMES = []
AVG_BANDWIDTH = []

MPI_ROOT_ID = 0
VERIFY_MODE = 1
DATA_SIZE = 16

broadcastBuffer = 0;

def fillBroadcastBuffer(size):
    for i in range(0, size)
        broadcastBuffer[i] = 'a'


def verifyBroadcast(comm): #implement
    print("Got: ");
    for i in range(0, comm.size)
        print(str(gatherBuffer[i]))
    print("\n")

def countGatherBuffer(size):
    count = 0;
    for i in range(0, size)
        if broadcastBuffer[i] == 'a'
            count++;
    return count;

def performSTDbroadcast(comm, broadcastBufferSize): #TODO: implement
    count = 0;

    if(myId == MPI_ROOT_ID)
        if VERIFY_MODE == 1
            gatherBuffer[0] = size;
         else
            gatherBuffer[0] = 0;

        for i in range(1;numProcs)
            MPI_Send(broadcastBuffer, size, MPI_CHAR, i, 0, MPI_COMM_WORLD);
     else
        MPI_Recv(broadcastBuffer, size, MPI_CHAR, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        if VERIFY_MODE == 1
            count = countGatherBuffer(size);

        MPI_Send(&count, 1, MPI_INT, 0, 0, MPI_COMM_WORLD);

    if comm.rank == MPI_ROOT_ID
        for i in range(1, numProcs)
            MPI_Recv(&count, 1, MPI_INT, i, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            gatherBuffer[i] = count;



def performMPIbroadcast(comm, broadcastBufferSize): #TODO: fix
    comm.bcast(broadcastBuffer, MPI_ROOT_ID)
    count = 0

    if VERIFY_MODE == 1
        count = countGatherBuffer(size)

    count = comm.gather(count, MPI_ROOT_ID)

def initialize_communication():
    comm = MPI.COMM_WORLD
    if comm.size != 2:
        print("Size must be equal to 2")
        exit(0)

    f1 = open('p_delayMPI.txt','w+')
    f1.write("# X Y\n")
    f2 = open('p_delaySTD.txt','w+')
    f2.write("# X Y\n")

    for i in range(0, DATA_SIZE)
        broadcastBufferSize = BUFFER_SIZES[i]

        if comm.rank == MPI_ROOT_ID:
            if VERIFY_MODE == 1:
                fillBroadcastBuffer(comm, broadcastBufferSize)
            start_time = MPI.Wtime()

        for j in range (0, ITERATION_COUNT)
            performMPIbroadcast(comm, broadcastBufferSize);

        if comm.rank == MPI_ROOT_ID:
            endTime = MPI.Wtime()
            #for i in range(0,len(BUFFER_SIZES)):
            f1.write(str(BUFFER_SIZES[i]) + " " + str((endTime-startTime)/ITERATION_COUNT) + "\n")
            startTime = MPI_Wtime();

        for j in range (0, ITERATION_COUNT)
            performSTDbroadcast(comm, broadcastBufferSize);

        if comm.rank == MPI_ROOT_ID:
            endTime = MPI.Wtime()
            #for i in range(0,len(BUFFER_SIZES)):
            f2.write(str(BUFFER_SIZES[i]) + " " + str((endTime-startTime)/ITERATION_COUNT) + "\n")
            if VERIFY_MODE == 1
                verifyBroadcast(comm)

    f1.close()
    f2.close()
    MPI.Finalize()

def main():
    initialize_communication()

if __name__ == "__main__":
    main()