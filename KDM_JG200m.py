import serial
import time
import threading
class KDM_JG200m(threading.Thread):

  def __init__(self, com='com3', com_rate=19200, cout=False):
    threading.Thread.__init__(self)
    self.cout = cout # true for console output
    self.filename = None
    self.com = com
    self.com_rate = com_rate
    self.buf = []
    self.t = None #last data receive time
    self.t0 = None # start receive time
    self.stopped = False
    self.distance = 0
    print('KDM_JG200m object is created.')

  def SerialStart(self):
    try:
      self.ser = serial.Serial(self.com, self.com_rate)#, timeout=0)
      if self.cout:
        print(self.ser)
      return True
    except:
      print('fail to open serial port:{}'.format(self.com))
      return False

  def run(self):
    if self.cout:
      print('KDM_JG200m thread is running.')
    self.com_OK = self.SerialStart()
    self.t0 = time.time() 
    i = 0
    
    while self.com_OK and not self.stopped:
      n = self.ser.in_waiting
      if n>8:
        rev = self.ser.read(n)
        if self.filename:
          self.t = time.time()
          self.buf.extend(rev)        
        index = [i for i,x in enumerate(rev) if x == 255][-1]
        self.distance = rev[index-2]*100+rev[index-1]
        if self.cout:
          print(self.distance<2900, n,rev[index],rev[index-2],rev[index-1])

  def stop(self): 
    self.SaveDistanceFile()
    self.stopped = True   
    print('KDM_JG200m thread is closing.')
    try:
      self.ser.close()
      print('close serial port:{}'.format(self.com))
    except:
      print('fail to close serial port:{}'.format(self.com))
      pass    
   
  def isStopped(self):
    return self.stopped  

  def SaveDistanceFile(self):
    if self.filename:
      print('save KDM_JG200m data to{}'.format(self.filename))
    else:
      return    

    if len(self.buf) == 0:
      if self.cout:
        print("No distance message")
      return


    index = [i for i,x in enumerate(self.buf) if x == 255]
    frame_num = len(index)
    if index[-1]<len(self.buf):#最后一帧没有收全
      frame_num += 1

    f = open(self.filename,'w')
    f.write('index,distance,time\n')
    delta_t = (self.t-self.t0)/frame_num
    frame_num = 0
    lost_num = 0
    for i,x in enumerate(index):
        if x>1:#如果第一帧不全就不处理了
            frame_t = self.t0 + i*delta_t
            distance = self.buf[x-2]*100+self.buf[x-1]
            if distance > 2900:
              lost_num = lost_num + 1
            frame_num = frame_num + 1
            s = '{i},{d},{t}\n'.format(i=i,d=distance, t=frame_t)
            f.write(s)  
    if self.cout:
      print("total num: {}, lost_num: {}".format(frame_num, lost_num))  
    f.close()
    self.filename = None




