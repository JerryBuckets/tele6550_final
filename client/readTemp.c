#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>

typedef int BMP280_S32_t;
unsigned short dig_T1;
short dig_T2;
short dig_T3;

BMP280_S32_t t_fine;
BMP280_S32_t bmp280_compensate_T_int32(BMP280_S32_t adc_T)
{
	BMP280_S32_t var1, var2, T;
	var1 = ((((adc_T>>3) - ((BMP280_S32_t)dig_T1<<1))) * ((BMP280_S32_t)dig_T2)) >> 11;
	var2 = (((((adc_T>>4) - ((BMP280_S32_t)dig_T1)) * ((adc_T>>4) - ((BMP280_S32_t)dig_T1))) >> 12) *
			((BMP280_S32_t)dig_T3)) >> 14;
	t_fine = var1 + var2;
	T = (t_fine * 5 + 128) >> 8;
	return T;
}


int main() {
	int config_reg = 0xf4;
	int id_reg = 0xd0;
	unsigned char msg[0x10];
	int addr = 0x76;
	int i2c_id = open("/dev/i2c-1", O_RDWR);
	ioctl(i2c_id, I2C_SLAVE, addr);

	msg[0] = config_reg;
	msg[1] = 0b10110111;
	write(i2c_id, msg, 2);
	msg[0] = id_reg;
	unsigned char resp[0x6];
	write(i2c_id, msg, 1);
	read(i2c_id, resp, 1);
	printf("Got ID of %x\n", resp[0]);

	msg[0] = 0x88;
	write(i2c_id, msg, 1);
	read(i2c_id, msg, 6);
	dig_T1 = msg[0] | (msg[1] << 8);
	dig_T2 = msg[2] | (msg[3] << 8);
	dig_T3 = msg[4] | (msg[5] << 8);

	printf("dig_T1= %d, dig_T2= %d, dig_T3= %d\n", dig_T1, dig_T2, dig_T3);

	int temp_reg = 0xfa;
	msg[0] = temp_reg;
	unsigned char temp_response[0x4];	
	int offset = 0xf0;
	
	//Setup Pipe

	int fifo_fd = -2;
	char * fifo = "/tmp/temp";
	int mkfifo_sucess;
	int access_sucess;

	access_sucess = access(fifo, W_OK);

	if(access_sucess != 0){
		mkfifo_sucess = mkfifo(fifo, 0666);
		printf("Made FIFO\n");
	}
	
	fifo_fd = open(fifo, O_WRONLY);
	
	if(fifo_fd < 0){
		printf("fifo_fd is %d\n", fifo_fd);
		printf("Unable to open FIFO\n");
	}

	char buf[10];

	for(;;) {
		msg[0] = 0xfa;
		write(i2c_id, msg, 1);
		read(i2c_id, temp_response, 3);
		int t3 = ((int)temp_response[2] & offset) >> 4;
		int t2 = (int)temp_response[1] << 4;
		int t1 = (int)temp_response[0] << 12;
		float temp = (float)bmp280_compensate_T_int32(t3 | t2 | t1)/100.0;
		printf("Temp= %.2f\n", temp);
		gcvt(temp, 4, buf);
		int status = write(fifo_fd, &buf, strlen(buf));
		printf("%d\n", status);
		usleep(500000);
	}
	close(i2c_id);
	close(fifo_fd);
	unlink(fifo);
	return 0;
}
