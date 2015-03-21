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

def save_delay_times():
    f = open('p_delay.txt','w+')
    f.write("# X Y\n")
    for i in range(0,len(BUFFER_SIZES)):
        f.write(str(BUFFER_SIZES[i]) + " " + str(AVG_DELAY_TIMES[i]) + "\n")
    f.close()


def save_bandwidth():
    f = open('p_bandwidth.txt','w+')
    f.write("# X Y\n")
    for i in range(0,len(BUFFER_SIZES)):
        f.write(str(BUFFER_SIZES[i]) + " " + str(AVG_BANDWIDTH[i]) + "\n")
    f.close()

def performMPIbroadccast(comm, broadcastBufferSize): #TODO: finish this
    return broadcastBufferSize

def fillBroadcastBuffer(comm, broadcastBufferSize): #TODO: finish this
    return broadcastBufferSize

def save_results(comm_type):
    save_delay_times(comm_type)
    save_bandwidth(comm_type)

def initialize_communication(comm_type):
    comm = MPI.COMM_WORLD
    if comm.size != 2:
        print("Size must be equal 2")
        exit(0)

    if comm.rank == MPI_ROOT_ID:
        if VERIFY_MODE == 1:
            fillBroadcastBuffer(comm, broadcastBufferSize)
        start_time = MPI.Wtime()

        for i in range(0, SEND_RECV_ITERATIONS):
            performMPIbroadcast(comm, broadcastBufferSize)

def main():
    initialize_communication(comm_type)

if __name__ == "__main__":
    main()