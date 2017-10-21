#!/usr/bin/env python
import struct
import time

def ReadIMU(filename, fmt, l):
  # read IMU data collected from wifi
  # 1 package per second, the time stamp is useful
  with open(filename, "rb") as f:
    data = f.read(l)
    while 1:
      try:
        u = struct.unpack(fmt, data)
        data = f.read(l)
        print(u[0])
      except:
        break

if __name__ == '__main__':
  ReadIMU("20171021_221426_imu.bin", "d2i20f", 96)
  #ReadIMU("20171021_221426.bin", "2i20f", 88)




 
