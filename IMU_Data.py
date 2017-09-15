import socket
import time
import threading
import struct
from math import asin, atan2, pi

class IMU_Data(threading.Thread):
  def __init__(self, filename=None, host='192.168.1.2', port=4210, cout=False):
    threading.Thread.__init__(self)
    self.cout = cout # true for console output
    self.filename = filename
    self.host = host
    self.port = port
    self.stopped = False
    self.s = None
    self.connected = False# socket is connected
    self.imu_data = [0.0 for i in range(20)]
    self.q = [0.0, 0.0, 0.0, 0.0]

  def connectIMU(self):
    try:
      self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.s.bind(("", self.port))
      print('Socket Created.')
      return True
    except:
      print('Failed to create socket.')
      return False      

  def run(self):
    self.connected = self.connectIMU()
    self.s.sendto(b'r',(self.host, self.port))# send a char to IMU server
    if self.filename:
      self.f = open(self.filename,'w')
    while not self.stopped and self.connected:
      data, addr = self.s.recvfrom(1024)
      self.ParseIMUData(data)
      if self.filename:
        t = time.time()
        #t = time.clock()#only for windows
        s = '{t},{d}\n'.format(t=t, d=data)
        self.f.write(s)

      if self.cout:
        print(data)
  def ParseIMUData(self, data):
    s = str(data, encoding = "utf-8").split(',')
    self.imu_data = [struct.unpack('<f', bytes.fromhex(h))[0] for h in s[:-1]]
    for i in range(4):
      self.q[i] = self.imu_data[i]

  def Quaternion(self):
    q = self.q

    a12 = 2.0 * (q[1]*q[2] + q[0]*q[3]);
    a22 = q[0] * q[0] + q[1]*q[1] - q[2]*q[2] - q[3]*q[3];
    a31 = 2.0 * (q[0]*q[1] + q[2]*q[3]);
    a32 = 2.0 * (q[1]*q[3] - q[0]*q[2]);
    a33 = q[0]*q[0] - q[1]*q[1] - q[2]*q[2] + q[3]*q[3];
    
    pitch = -asin(a32);
    roll  = atan2(a31, a33);
    yaw   = atan2(a12, a22);
    pitch *= 180.0 / pi;
    yaw   *= 180.0 / pi; 
    yaw   += 13.8; # Declination at Danville, California is 13 degrees 48 minutes and 47 seconds on 2014-04-04
    if yaw < 0:
      yaw += 360.0; # Ensure yaw stays between 0 and 360
    roll *= 180.0 / pi;
    return yaw, pitch, roll

  def stop(self): 
    self.stopped = True

  def isStopped(self):
    if self.filename:
      self.f.close()
    return self.stopped 

