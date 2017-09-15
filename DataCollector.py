#!/usr/bin/env python
'''
Real-time plot demo using sine waves.

Copyright (C) 2015 Simon D. Levy

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
'''

from realtime_plot import RealtimePlotter
import numpy as np
import time
from KDM_JG200m import KDM_JG200m
from IMU_Data import IMU_Data
import threading
from time import sleep

class DataPlotter(RealtimePlotter):

    def __init__(self):

        RealtimePlotter.__init__(self)

        self.distance = 0.0
        self.imu_data = [0.0 for i in range(20)]

    def getValues(self):
        #yaw, pitch, roll = imu_thread.Quaternion()
        # print(x,y,z)
        return (self.imu_data, self.distance)

def _update(plotter, dis_thread):  

    while True:
        plotter.distance = float(dis_thread.distance)/100
        #print(imu_thread.imu_data)
        plotter.imu_data = imu_thread.imu_data
        sleep(.002)



if __name__ == '__main__':
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



 
