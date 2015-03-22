#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

#define MPI_ROOT_ID 0

#define DATA_SIZE 16			// rozmiar tablicy z różnymi rozmiarami danych
#define ITERATION_COUNT 100		// ilość powtórzeń komunikacji (celem uśrednienia statystyk)

#define VERIFY_MODE 1			// opcja ustalająca, czy weryfikować poprawność przesyłanych danych (0 - off, 1 - on) - (po testach: nie ma różnicy)


/* globals */
int numProcs, myId, mpi_err;

int iterationData[DATA_SIZE] = {1000, 5000, 10000, 20000, 30000, 50000, 100000, 200000, 300000, 500000, 1000000, 2000000, 3000000, 5000000, 6000000, 10000000};
char* broadcastBuffer;
int* gatherBuffer;

//FILE* delayMPIfile;
//FILE* delayMYFile;
FILE* bandwidthMPIfile;
FILE* bandwidthMyFile;
/* end globals  */

/* helper function declarations */
void initMPI(int, char**);
void prepareBuffers();
void openFiles();
void reallocBrodcastBuffer(int broadcastBufferSize);
void fillBroadcastBuffer(int broadcastBufferSize);
int countGatherBuffer();
void performMPIbroadcast(int broadcastBufferSize);
void performMyBroadcast(int broadcastBufferSize);
void freeBuffers();
void closeFiles();
void verifyBroadcast();
/* end helper function declarations */

int main(int argc, char** argv) {
	initMPI(argc, argv);

	int i, j;
	int count;
	int broadcastBufferSize;

	double startTime, endTime;

	prepareBuffers();
	openFiles();

	for(i=0; i<DATA_SIZE; i++) {
		broadcastBufferSize = iterationData[i];
		reallocBrodcastBuffer(broadcastBufferSize);

		if(myId == MPI_ROOT_ID) {
			if(VERIFY_MODE) {
				fillBroadcastBuffer(broadcastBufferSize);
			}
			startTime = MPI_Wtime();
		}

		for(j=0; j<ITERATION_COUNT; j++) {
			performMPIbroadcast(broadcastBufferSize);
		}

		if(myId == MPI_ROOT_ID) {
			endTime = MPI_Wtime();
			fprintf(bandwidthMPIfile, "%d %f\n", broadcastBufferSize, (endTime-startTime)/ITERATION_COUNT);
			startTime = MPI_Wtime();
		}

		for(j=0; j<ITERATION_COUNT; j++) {
			performMyBroadcast(broadcastBufferSize);
		}

		if(myId == MPI_ROOT_ID) {
			endTime = MPI_Wtime();
			fprintf(bandwidthMyFile, "%d %f\n", broadcastBufferSize, (endTime-startTime)/ITERATION_COUNT);
			if(VERIFY_MODE) {
				verifyBroadcast();
			}
		}
	}

	freeBuffers();
	closeFiles();

	MPI_Finalize();
}

/* helper function decfinitions */
void initMPI(int argc, char** argv) {
	MPI_Init(&argc, &argv);
	MPI_Comm_size(MPI_COMM_WORLD, &numProcs);
	MPI_Comm_rank(MPI_COMM_WORLD, &myId);
}

void prepareBuffers() {
	broadcastBuffer = (char*)malloc(1*sizeof(char));
	gatherBuffer = (int*)malloc(numProcs*sizeof(int));
}

void openFiles() {
	char filenameBuffer[25];
//	sprintf(filenameBuffer, "c_delay_mpi_%d.txt", numProcs);
//	delayMPIfile = fopen(filenameBuffer, "w");
//	sprintf(filenameBuffer, "c_delay_my_%d.txt", numProcs);
//	delayMYFile = fopen(filenameBuffer, "w");
	sprintf(filenameBuffer, "c_bandwidth_mpi_%d.txt", numProcs);
	bandwidthMPIfile = fopen(filenameBuffer, "w");
	fprintf(bandwidthMPIfile, "#processors: %d\n", numProcs);
	fprintf(bandwidthMPIfile, "#data_size[B] time[s]\n");

	sprintf(filenameBuffer, "c_bandwidth_my_%d.txt", numProcs);
	bandwidthMyFile = fopen(filenameBuffer, "w");
	fprintf(bandwidthMyFile, "#processors: %d\n", numProcs);
	fprintf(bandwidthMyFile, "#data_size[B] time[s]\n");
}

void reallocBrodcastBuffer(int size) {
	broadcastBuffer = (char*)(realloc(broadcastBuffer, size));
}

void fillBroadcastBuffer(int size) {
	int i;
	for(i=0; i<size; i++) {
		broadcastBuffer[i] = 'a';
	}
}

int countGatherBuffer(int size) {
	int i;
	int count=0;
	for(i=0; i<size; i++) {
		if(broadcastBuffer[i] == 'a') {
			count++;
		}
	}

	return count;
}

void performMPIbroadcast(int size) {
	MPI_Bcast(broadcastBuffer, size, MPI_CHAR, 0, MPI_COMM_WORLD);
	int count = 0;

	if(VERIFY_MODE) {
		count = countGatherBuffer(size);
	}
	MPI_Gather(&count, 1, MPI_INT, gatherBuffer, 1, MPI_INT, 0, MPI_COMM_WORLD);
}

void performMyBroadcast(int size) {
	int i;
	int count = 0;

	if(myId == MPI_ROOT_ID) {
		if(VERIFY_MODE) {
			gatherBuffer[0] = size;
		} else {
			gatherBuffer[0] = 0;
		}
		for(i=1; i<numProcs; i++) {
			MPI_Send(broadcastBuffer, size, MPI_CHAR, i, 0, MPI_COMM_WORLD);
		}
	} else {
		MPI_Recv(broadcastBuffer, size, MPI_CHAR, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
		if(VERIFY_MODE) {
			count = countGatherBuffer(size);
		}
		MPI_Send(&count, 1, MPI_INT, 0, 0, MPI_COMM_WORLD);
	}
	if(myId == MPI_ROOT_ID) {
		for(i=1; i<numProcs; i++) {
			MPI_Recv(&count, 1, MPI_INT, i, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
			gatherBuffer[i] = count;
		}
	}
}

void freeBuffers() {
	free(broadcastBuffer);
	free(gatherBuffer);
}

void closeFiles() {
//	fclose(delayMPIfile);
//	fclose(delayMYFile);
	fclose(bandwidthMPIfile);
	fclose(bandwidthMyFile);
}


void verifyBroadcast() {
	int i;
	printf("Got: ");
	for(i=0; i<numProcs; i++) {
		printf("%d ", gatherBuffer[i]);
	}
	printf("\n");
}
/* end helper function decfinitions */

