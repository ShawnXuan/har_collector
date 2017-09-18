import socket
import time
import threading
import struct
from math import asin, atan2, pi

def del_file(p):
  """Delete a file."""
  if path.isfile(p):
    os.remove(p)
    print('F : %s' % p)

class IMU_Data(threading.Thread):
  def __init__(self, host='192.168.1.2', port=4210, cout=False):
    threading.Thread.__init__(self)
    self.cout = cout # true for console output
    self.filename = None
    self.str_t = None
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
    if self.str_t == None:
      return

    if not self.connected: 
      self.connected = self.connectIMU()
    if not self.connected:
      return

    cmd = "Start:"+self.str_t
    cmd = bytes(cmd, encoding = "utf8")  
    self.s.sendto(cmd,(self.host, self.port))# send a char to IMU server
    self.filename = self.str_t+"_imu.csv"

    self.f = open(self.filename,'w')
    while not self.stopped and self.connected:
      data, addr = self.s.recvfrom(1024)
      #nbytes, add = self.s.recvfrom_into(data)
      print(data)
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
    print("stop", self.str_t)
    if self.str_t:
      if self.connected:
        cmd = "Stop:"+self.str_t
        cmd = bytes(cmd, encoding = "utf8") 
        self.s.sendto(cmd,(self.host, self.port))# send a char to IMU server
      self.f.close()
      self.str_t = None
    else:
      if self.connected:
        cmd = "Abort:"+self.str_t
        cmd = bytes(cmd, encoding = "utf8") 
        self.s.sendto(cmd,(self.host, self.port))# send a char to IMU server
      print(self.filename)
      if self.filename:
        self.f.close()
        del_file(self.filename)    
    self.stopped = True
    self.str_t = None


  def isStopped(self):
    print("isStopped", self.str_t)
    self.filename = None  
    self.str_t = None
    return self.stopped 

