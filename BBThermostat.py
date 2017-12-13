import os
import glob
import time
import urllib2

#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')
device_file = glob.glob('/sys/bus/w1/devices/28*')[0] + '/w1_slave'

def read_temp():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()

    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
    return 0

if __name__ == "__main__":
    while True:
        time.sleep(2)
        temp = read_temp()
        r = urllib2.urlopen("http://192.168.0.19/thermometer/" + str(temp)).read()
        print temp, r
        # do somekind of test on r and logging
