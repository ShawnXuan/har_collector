#!/usr/bin/env python
import struct
import time
#from sklearn.linear_model import LinearRegression 
import numpy as np
import csv
import pandas as pd

def ReadIMU(filename, fmt, l):
  # read IMU data collected from wifi/SD Card
  # 1 package per second, the time stamp is useful
  with open(filename, "rb") as f:
    data = f.read(l)
    while 1:
      try:
        u = struct.unpack(fmt, data)
        data = f.read(l)
        print(u[0], u[1], u[2])
      except:
        break


def StampTimeRegression(filename):
  fmt = "d2i20f"
  l = 96
  with open(filename, "rb") as f:
    data = f.read(l)
    x = []
    y = []
    while 1:
      try:
        u = struct.unpack(fmt, data)
        x.append(u[1])
        y.append(u[0])
        data = f.read(l)
        #print(u[0], u[1])
      except:
        break  
  n = len(x)
  x = np.array(x)
  y = np.array(y)

  x_ = np.mean(x)
  y_ = np.mean(y)

  xy = np.sum(x * y)
  xx = np.sum(x * x)
  
  a = (xy - n*x_*y_)/(xx - n*x_*x_)
  b = y_-a*x_
  print("y = ax+b", a, b)
  return(a, b)

def CreateDataBin(src, dst, dis, a, b):
  df=pd.read_csv(dis)
  times = df['time'].values, 
  distances = df['distance'].values

  dst_file = open(dst, "wb")
  fmt = "2i20f"
  l = 88
  with open(src, "rb") as f:
    data = f.read(l)
    x = []
    y = []
    while 1:
      try:
        u = struct.unpack(fmt, data)        
        t = a*u[0] + b       

        bt = struct.pack('d', t)
        dst_file.write(bt);

        idx = np.argmin(np.abs(times - t))
        bd = struct.pack('i', distances[idx])        
        dst_file.write(bd)

        dst_file.write(data)
        data = f.read(l)
      except:
        break 
  dst_file.close()
def LoadDistance(filename):
  df=pd.read_csv(filename)
  #print(df)
  #print(df['distance'])
  return(df['time'].values, df['distance'].values)

  #with open(filename, "r") as csvfile:
  #  reader = csv.reader(csvfile, delimiter=',')
  #  for row in reader:
      #distance = float(txt[1])/100.0
      #time = float(txt[2])
  #    print(row)

if __name__ == '__main__':
  #ReadIMU("D:\HAR\Data\\20171021_221426_imu.bin", "d2i20f", 96)
  #ReadIMU("20171021_221426.bin", "2i20f", 88)
  #times, distances = LoadDistance("D:\HAR\Data\\20171021_221426_Distance.csv")
  #idx = np.argmin(np.abs(times - 1508595266.2577041))
  #print(idx)
  a, b = StampTimeRegression("D:\HAR\Data\\20171021_221426_imu.bin")
  CreateDataBin("D:\HAR\Data\\20171021_221426.csv", 
                "D:\HAR\Data\\20171021_221426.bin",
                "D:\HAR\Data\\20171021_221426_Distance.csv",
                a, b)

  

