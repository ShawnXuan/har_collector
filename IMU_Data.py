import socket
import time
import threading
import struct
import os
from math import asin, atan2, pi

def del_file(p):
  """Delete a file."""
  if os.path.isfile(p):
    os.remove(p)
    #print('F : %s' % p)

class IMU_Data(threading.Thread):
  def __init__(self, host='192.168.1.2', port=4210, cout=False):
    threading.Thread.__init__(self)
    self.cout = cout # true for console output
    self.filename = ""
    self.str_t = ""
    self.host = host
    self.port = port
    self.stopped = False
    self.s = None
    self.connected = False# socket is connected
    self.imu_data = [0.0 for i in range(20)]
    
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
    # specify the start time before run the thread
    if self.str_t == None:
      return

    if not self.connected: 
      self.connected = self.connectIMU()
    if not self.connected:
      print("fail to connect IMU")
      return

    cmd = "Start:"+self.str_t
    cmd = bytes(cmd, encoding = "utf8")  
    self.s.sendto(cmd,(self.host, self.port))# send a char to IMU server
    self.filename = self.str_t+"_imu.csv"

    self.f = open(self.filename,'w')
    while self.connected:
      try:
        data, addr = self.s.recvfrom(1024)
        print(data)
      except:
        self.s.close()
        print('udp closed')
      #nbytes, add = self.s.recvfrom_into(data)
      
      #self.ParseIMUData(data)
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

  def stop(self): 
    print("stop", self.str_t)
    if self.filename:
      self.f.close()    
    if self.delete_file:
      cmd = "Abort:"+self.str_t
      del_file(self.filename) 
    else:
      cmd = "Stop:"+self.str_t
      

    self.filename = ""
    self.connected = False    
    cmd = bytes(cmd, encoding = "utf8") 
    self.s.sendto(cmd,(self.host, self.port))

    self.stopped = True
    self.str_t = ""
    try:
      self.s.close()
    except:
      print('fail to close udp')

  def isStopped(self):
    return self.stopped 

