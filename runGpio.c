#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdint.h>
#include <arpa/inet.h>
#include <math.h>
#include <time.h>

#define BLINK 500000
#define SOLID 10000

int main() {
	int fd = open("/dev/mem", O_RDWR|O_SYNC);
	if (fd == -1) {
		printf("cannot open driver!\n");
		return -1;
	}

	printf("Here\n");
	//SELECT0
	uint32_t *gpio = mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0xfe200000);

	*gpio = 1 << 15; // GPIO 5 as output
	
	time_t last_time = time(NULL);

	int fifo_fd;
	char * fifo = "/tmp/gpio";
	int mkfifo_sucess;
	int access_sucess;

	access_sucess = access(fifo, W_OK);

	if(access_sucess != 0){
		mkfifo_sucess = mkfifo(fifo, 0666);
		printf("Made FIFO\n");
	}

	fifo_fd = open(fifo, O_RDONLY | O_NONBLOCK);

	if(fifo_fd < 0) {
		printf("Unable to open FIFO\n");
	}
	
	int flags = fcntl(fifo_fd, F_GETFL, 0);
	fcntl(fifo_fd, F_SETFL, flags | O_NONBLOCK);

	int recieved;
	int state = 0;
	int sleep_time;


	while(1){
		ssize_t bytes_read = read(fifo_fd, &recieved, sizeof(recieved));
		if(bytes_read){

			//BLINK
			if (recieved == 2){
				printf("IN STATE BLINK\n");
				state = 2;
				sleep_time = BLINK;
			//OFF
			}else if (recieved == 0){
				printf("IN STATE OFF\n");
				state = 0;

			//SOLID
			} else if (recieved == 1){
				printf("IN STATE SOLID\n");
				state = 1;
				sleep_time = SOLID;
			} else {}
		}
		
		last_time = time(NULL);
		while (last_time + (time_t)2 > time(NULL)){
			if (state == 0) {
				*(gpio + 10) = (1 << 5);
				usleep(1000000);
			}
			else {
				*(gpio + 7) = (1 << 5); // GPIO 5 ON
				usleep(sleep_time);
				*(gpio + 10) = (1 << 5); // GPIO 5 OFF
				usleep(sleep_time);
			}
		}

	}
	
			
	return 0;
}

