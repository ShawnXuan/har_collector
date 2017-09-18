#!/usr/bin/env python

from realtime_plot import RealtimePlotter
import numpy as np
import time
from KDM_JG200m import KDM_JG200m
from IMU_Data import IMU_Data
import threading
from time import sleep

from tkinter import *

class Application(Frame):
    def start(self):
        t = time.localtime()
        str_t = time.strftime("%Y%m%d_%H%M%S", t)

        #self.dis_thread = KDM_JG200m(cout=False)
        #self.dis_thread.filename = str_t + "_Distance.csv"
        #self.dis_thread.start()
        
        self.imu_thread = IMU_Data(cout=False)
        self.imu_thread.str_t = str_t
        self.imu_thread.start()
        print("Start recording on !",str_t)

    def stop(self):
        #self.dis_thread.stop()
        #self.dis_thread.join()
        self.imu_thread.stop()
        self.imu_thread.join()
        print("Stop recording!")

    def abort(self):
        #self.dis_thread.filename = None
        #self.dis_thread.stop()
        #self.dis_thread.join()        
        self.imu_thread.filename = None
        self.imu_thread.stop()
        self.imu_thread.join()        
        print("Abort recording!")

    def createWidgets(self):
        self.btnStart = Button(self)
        self.btnStart["text"] = "Start"
        self.btnStart["command"] =  self.start
        self.btnStart.grid(row=1, column=0)

        self.btnStop = Button(self)
        self.btnStop["text"] = "Stop"
        self.btnStop["command"] =  self.stop
        self.btnStop.grid(row=1, column=1)

        self.btnAbort = Button(self)
        self.btnAbort["text"] = "Abort"
        self.btnAbort["command"] =  self.abort
        self.btnAbort.grid(row=1, column=2)

    def __init__(self, master=None, dis_thread=None):
        Frame.__init__(self, master)
        self.dis_thread = dis_thread
        self.pack()
        self.createWidgets()

if __name__ == '__main__':
    root = Tk()
    app = Application(master=root)
    app.mainloop()
    #root.destroy()

    '''
    t = time.localtime()
    dis_filename =time.strftime("%Y%m%d_%H%M%S_Distance.csv", t)
    dis_thread = KDM_JG200m(filename=dis_filename, cout=False)
    dis_thread.start()

    imu_filename =time.strftime("%Y%m%d_%H%M%S_IMU.csv", t)
    imu_thread = IMU_Data(filename=imu_filename, cout=False)
    # imu_thread = IMU_Data(filename=imu_filename, 
    #                     host='172.31.18.112', 
    #                     cout=False)
    imu_thread.start()

    plotter = DataPlotter()

    thread = threading.Thread(target=_update, args = (plotter, dis_thread))
    thread.daemon = True
    thread.start()

    plotter.start()

    dis_thread.stop()
    dis_thread.join()

    imu_thread.stop()
    imu_thread.join()
    '''



 
