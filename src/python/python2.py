__author__ = 'bkumor'
from mpi4py import MPI
import socket
import sys
from array import array

SEND_RECV_ITERATIONS = 100
BUFFER_SIZES = [1000, 5000, 10000, 20000, 30000, 50000, 100000,
                200000, 300000, 500000, 1000000, 2000000, 3000000,
                5000000, 6000000, 10000000]

AVG_DELAY_TIMES = []
AVG_BANDWIDTH = []

MPI_ROOT_ID = 0
VERIFY_MODE = 1
DATA_SIZE = 16

#broadcastBuffer = array('c')



def fillBroadcastBuffer(size, broadcastBuffer):
    for i in range(0, size):
        broadcastBuffer.append('a')
    return broadcastBuffer


def verifyBroadcast(comm, gatherBuffer):
    print("Got: ")
    for i in range(0, comm.size):
        print(str(gatherBuffer[i]))
    print("\n")


def countGatherBuffer(size, broadcastBuffer):
    count = 0
    for i in range(0, size):
        if broadcastBuffer[i] == 'a':
            count = count + 1
    return count


def performSTDbroadcast(comm, broadcastBufferSize, broadcastBuffer):
    count = 0
    gatherBuffer = array('i')
    if(comm.rank == MPI_ROOT_ID):
        if VERIFY_MODE == 1:
            gatherBuffer.append(broadcastBufferSize)
        else:
            gatherBuffer.append(0)

        for i in range(1, comm.size):
            comm.send(broadcastBuffer, i)
    else:
        data = comm.recv(source = 0)
        if VERIFY_MODE == 1:
            count = countGatherBuffer(broadcastBufferSize, gatherBuffer)

        comm.send(count, 0)

    if comm.rank == MPI_ROOT_ID:
        for i in range(1, comm.size):
            count = comm.recv(source = i)
            gatherBuffer.append(count)

    return gatherBuffer

def performMPIbroadcast(comm, broadcastBufferSize, broadcastBuffer): #TODO: fix
    comm.bcast(broadcastBuffer, MPI_ROOT_ID)
    count = 0

    if VERIFY_MODE == 1:
        count = countGatherBuffer(broadcastBufferSize, broadcastBuffer)

    count = comm.gather(count, MPI_ROOT_ID)


def initialize_communication():
    comm = MPI.COMM_WORLD
    f1 = open('p_delayMPI' + str(comm.size) + '.txt','w+')
    f1.write('#number_of_processors: ' + str(comm.size) + '\n')
    f1.write("#data_size[B] time[s]\n")
    f2 = open('p_delaySTD' + str(comm.size) + '.txt','w+')
    f2.write('#number_of_processors: ' + str(comm.size) + '\n')
    f2.write("#data_size[B] time[s]\n")
    for i in range(0, DATA_SIZE):
        broadcastBufferSize = BUFFER_SIZES[i]
        if comm.rank == MPI_ROOT_ID:
            if VERIFY_MODE == 1:
                data = array('c')
                data = fillBroadcastBuffer(broadcastBufferSize, data)
            startTime = MPI.Wtime()

        for j in range (0, SEND_RECV_ITERATIONS):
            performMPIbroadcast(comm, broadcastBufferSize, data)

        if comm.rank == MPI_ROOT_ID:
            endTime = MPI.Wtime()
            f1.write(str(BUFFER_SIZES[i]) + " " + str((endTime-startTime)/SEND_RECV_ITERATIONS) + "\n")
            startTime = MPI.Wtime()
        gatherBuffer = array('i')
        for j in range (0, SEND_RECV_ITERATIONS):
            gatherBuffer = performSTDbroadcast(comm, broadcastBufferSize, data)

        if comm.rank == MPI_ROOT_ID:
            endTime = MPI.Wtime()
            f2.write(str(BUFFER_SIZES[i]) + " " + str((endTime-startTime)/SEND_RECV_ITERATIONS) + "\n")
            if VERIFY_MODE == 1:
                verifyBroadcast(comm, gatherBuffer)

    f1.close()
    f2.close()
    MPI.Finalize()


def main():
    initialize_communication()

if __name__ == "__main__":
    main()