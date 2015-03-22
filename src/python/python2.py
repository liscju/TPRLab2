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
    broadcastBuffer = comm.bcast(broadcastBuffer, MPI_ROOT_ID)
    count = 0

    if VERIFY_MODE == 1:
        count = countGatherBuffer(broadcastBufferSize, broadcastBuffer)

    count = comm.gather(count, MPI_ROOT_ID)

def invoke_and_calculate_time(fun):
    start_time = MPI.Wtime()
    retVal = fun()
    end_time = MPI.Wtime()
    return (end_time - start_time),retVal


def open_mpi_file(comm):
    f1 = open('p_delayMPI' + str(comm.size) + '.txt', 'w+')
    f1.write('#number_of_processors: ' + str(comm.size) + '\n')
    f1.write("#data_size[B] time[s]\n")
    return f1


def open_std_file(comm):
    f2 = open('p_delaySTD' + str(comm.size) + '.txt', 'w+')
    f2.write('#number_of_processors: ' + str(comm.size) + '\n')
    f2.write("#data_size[B] time[s]\n")
    return f2


def iterate_performMPIbroadcast(broadcastBufferSize, comm, data):
    for j in range(0, SEND_RECV_ITERATIONS):
        performMPIbroadcast(comm, broadcastBufferSize, data)


def iterate_performSTDbroadcast(broadcastBufferSize, comm, data):
    for j in range(0, SEND_RECV_ITERATIONS):
        performSTDbroadcast(comm, broadcastBufferSize, data)


def mpi_communication(broadcastBufferSize, comm, data, mpi_file):
    if comm.rank == MPI_ROOT_ID:
        execution_time,_ = invoke_and_calculate_time(
            lambda: iterate_performMPIbroadcast(broadcastBufferSize, comm, data)
        )
        mpi_file.write(str(broadcastBufferSize) + " " + str(execution_time / SEND_RECV_ITERATIONS) + "\n")
    else:
        iterate_performMPIbroadcast(broadcastBufferSize, comm, data)


def std_communication(broadcastBufferSize, comm, data, std_file):
    if comm.rank == MPI_ROOT_ID:
        gatherBuffer = array('i')
        execution_time,gatherBuffer = invoke_and_calculate_time(
            lambda: iterate_performSTDbroadcast(broadcastBufferSize, comm, data)
        )
        std_file.write(str(broadcastBufferSize) + " " + str(execution_time / SEND_RECV_ITERATIONS) + "\n")
        if VERIFY_MODE == 1:
            verifyBroadcast(comm,gatherBuffer)
    else:
        iterate_performSTDbroadcast(broadcastBufferSize, comm, data)


def initialize_data(broadcastBufferSize, comm):
    data = None
    if comm.rank == MPI_ROOT_ID:
        if VERIFY_MODE == 1:
            data = array('c')
            data = fillBroadcastBuffer(broadcastBufferSize, data)
    return data


def initialize_communication():
    comm = MPI.COMM_WORLD
    mpi_file = open_mpi_file(comm)
    std_file = open_std_file(comm)
    for i in range(0, DATA_SIZE):
        broadcastBufferSize = BUFFER_SIZES[i]
        data = initialize_data(broadcastBufferSize, comm)
        mpi_communication(broadcastBufferSize, comm, data, mpi_file)
        std_communication(broadcastBufferSize, comm, data, std_file)

    mpi_file.close()
    std_file.close()
    MPI.Finalize()


def main():
    initialize_communication()

if __name__ == "__main__":
    main()