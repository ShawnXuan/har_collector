'''
Real-time scrolling multi-plot over time.

Requires: matplotlib
          numpy

Adapted from example in http://stackoverflow.com/questions/8955869/why-is-plotting-with-matplotlib-so-slow

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

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
import numpy as np

# draw a vector
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d

def quaternion_mult(q,r):
    return [r[0]*q[0]-r[1]*q[1]-r[2]*q[2]-r[3]*q[3],
            r[0]*q[1]+r[1]*q[0]-r[2]*q[3]+r[3]*q[2],
            r[0]*q[2]+r[1]*q[3]+r[2]*q[0]-r[3]*q[1],
            r[0]*q[3]-r[1]*q[2]+r[2]*q[1]+r[3]*q[0]]

def point_rotation_by_quaternion(point,q):
    r = [0]+point
    q_conj = [q[0],-1*q[1],-1*q[2],-1*q[3]]
    return quaternion_mult(quaternion_mult(q,r),q_conj)[1:]

class Arrow3D(FancyArrowPatch):

    def __init__(self, v, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0, 0), (0, 0), *args, **kwargs)
        self._verts3d = [0,v[0]], [0,v[1]], [0,v[2]]
        
    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        FancyArrowPatch.draw(self, renderer)

    def set(self, v):
        self._verts3d = [0,v[0]], [0,v[1]], [0,v[2]]

class RealtimePlotter(object):
    '''
    Real-time scrolling multi-plot over time.  Your data-acquisition code should run on its own thread,
    to prevent blocking / slowdown.
    '''
    def handleClose(self, event):
        '''
        Automatically called when user closes plot window.
        Override to do you own shutdown.
        '''

        self.is_open = False

    def __init__(self):
        size=100 #size of display (X axis) in arbitrary time steps
        window_name = 'HAR Data Collector' #name to display at the top of the figure
        interval_msec=20 #animation update in milliseconds
        styles='b-'
        ylabels=''
        yticks=[]
        legends=[]
        ylims = []

        self.legends  = legends

        self.fig = plt.gcf()

        
        # Set up subplots
        # self.axes = [None]*7
        gs = GridSpec(3, 3)
        self.axes_acc = plt.subplot(gs[0,0])
        self.axes_gyr = plt.subplot(gs[1,0])
        self.axes_meg = plt.subplot(gs[2,0])
        self.axes_qua = plt.subplot(gs[0:2,1:3], projection='3d')
        self.axes_tem = plt.subplot(gs[2,1])
        self.axes_dis = plt.subplot(gs[2,2])

        # self.axes_acc = plt.subplot(gs[0,0])
        # self.axes_gyr = plt.subplot(gs[1,0])
        # self.axes_meg = plt.subplot(gs[2,0])
        # self.axes_qua = plt.subplot(gs[0,1], projection='3d')
        # self.axes_tem = plt.subplot(gs[1,1])
        # self.axes_pre = plt.subplot(gs[2,1])
        # self.axes_dis = plt.subplot(gs[:,2])

        # self.axes[0] = self.axes_acc
        # self.axes[1] = self.axes_gyr
        # self.axes[2] = self.axes_meg
        # self.axes[3] = self.axes_qua
        # self.axes[4] = self.axes_tem
        # self.axes[5] = self.axes_dis
        # self.axes[5] = self.axes_pre

        self.axes_dis.set_ylim(0,50)
        self.axes_acc.set_ylim(-2,2)
        self.axes_gyr.set_ylim(-100,100)
        self.axes_meg.set_ylim(-2000,1000)
        self.axes_tem.set_ylim(0,50)

        self.axes_qua.set_aspect("equal")
        self.axes_qua.set_xlim(-1,1)
        self.axes_qua.set_ylim(-1,1)
        self.axes_qua.set_zlim(-1,1)
        self.vx = Arrow3D([1,0,0], mutation_scale=10,
                    lw=1, arrowstyle="-|>", color="r")
        self.vy = Arrow3D([0,1,0], mutation_scale=10,
                    lw=1, arrowstyle="-|>", color="g")
        self.vz = Arrow3D([0,0,1], mutation_scale=10,
                    lw=1, arrowstyle="-|>", color="b")
        self.axes_qua.add_artist(self.vx)
        self.axes_qua.add_artist(self.vy)
        self.axes_qua.add_artist(self.vz)


        if window_name:
            self.fig.canvas.set_window_title(window_name)

        # Set up handler for window-close events
        self.fig.canvas.mpl_connect('close_event', self.handleClose)
        self.is_open = True

        # X values are arbitrary ascending; Y is initially zero
        self.x = np.arange(0, size)
        y = np.zeros(size)

        # Create lines
        self.lines = []
        self.lines.append(self.axes_acc.plot(self.x, y, 'r-', animated=True)[0])
        self.lines.append(self.axes_acc.plot(self.x, y, 'g-', animated=True)[0])
        self.lines.append(self.axes_acc.plot(self.x, y, 'b-', animated=True)[0])
        
        self.lines.append(self.axes_gyr.plot(self.x, y, 'r-', animated=True)[0])
        self.lines.append(self.axes_gyr.plot(self.x, y, 'g-', animated=True)[0])
        self.lines.append(self.axes_gyr.plot(self.x, y, 'b-', animated=True)[0])
        
        self.lines.append(self.axes_meg.plot(self.x, y, 'r-', animated=True)[0])
        self.lines.append(self.axes_meg.plot(self.x, y, 'g-', animated=True)[0])
        self.lines.append(self.axes_meg.plot(self.x, y, 'b-', animated=True)[0])
        
        self.lines.append(self.axes_tem.plot(self.x, y, 'g-', animated=True)[0])
        self.lines.append(self.axes_tem.plot(self.x, y, 'r-', animated=True)[0])

        #self.lines.append(self.axes_pre.plot(self.x, y, 'r-', animated=True)[0])
        #self.lines.append(self.axes_pre.plot(self.x, y, 'g-', animated=True)[0])
        
        self.lines.append(self.axes_dis.plot(self.x, y, 'b-', animated=True)[0])

        # Create baselines, initially hidden
        #self.baselines = [ax.plot(self.x, y, 'k', animated=True)[0] for ax in self.axes]
        #self.baseflags = [False]*nrows

        # Add properties as specified
        #[ax.set_ylabel(ylabel) for ax, ylabel in zip(self.axes, ylabels)]

        # Set axis limits
        #[ax.set_xlim((0,size)) for ax in self.axes]
        #[ax.set_ylim(ylim) for ax,ylim in zip(self.axes,ylims)]

        # Set ticks and gridlines
        #[ax.yaxis.set_ticks(ytick) for ax,ytick in zip(self.axes,yticks)]
        #[ax.yaxis.grid(True if yticks else False) for ax in self.axes]

        # XXX Hide X axis ticks and labels for now
        #[ax.xaxis.set_visible(False) for ax in self.axes]

        # Allow interval specification
        self.interval_msec = interval_msec

    def start(self):
        '''
        Starts the realtime plotter.
        '''

        ani = animation.FuncAnimation(self.fig, self._animate, interval=self.interval_msec, blit=True)
        #ani = animation.FuncAnimation(self.fig, self._animate, interval=10)
        try:
            plt.show()
        except:
            pass
  
    def getValues(self):
        '''
        Override this method to return actual Y values at current time.
        '''

        return None

    def showBaseline(self, axid, value):
        '''
        Shows a baseline of specified value for specified row of this multi-plot.
        '''

        self._axis_check(axid)

        self.baselines[axid].set_ydata(value * np.ones(self.x.shape))
        self.baseflags[axid] = True

    def hideBaseline(self, axid):
        '''
        Hides the baseline for the specified row of this multi-plot.
        '''

        self._axis_check(axid)

        self.baseflags[axid] = False

    def _axis_check(self, axid):

        nrows = len(self.lines)

        if axid < 0 or axid >= nrows:

            raise Exception('Axis index must be in [0,%d)' % nrows)

    @classmethod
    def roll(cls, getter, setter, line, newval):
        data = getter(line)
        data = np.roll(data, -1)
        data[-1] = newval
        setter(data)

    @classmethod
    def rollx(cls, line, newval):
        RealtimePlotter.roll(line.get_xdata, line.set_xdata, line, newval)

    @classmethod
    def rolly(cls, line, newval):
        RealtimePlotter.roll(line.get_ydata, line.set_ydata, line, newval)

    def _animate(self, t):
        imu_data, distance = self.getValues()
        values = [imu_data[4],  imu_data[5],  imu_data[6], # acc
                imu_data[7],  imu_data[8],  imu_data[9], # gry
                imu_data[10], imu_data[11], imu_data[12], # mag
                imu_data[16], imu_data[17], #imu_data[18],imu_data[19],  
                distance]
        x = [1, 0, 0] 
        y = [0, 1, 0]
        z = [0, 0, 1]
        q = [0.0, 0.0, 0.0, 0.0]
        for i in range(4):
            q[i] = imu_data[i]
        x = point_rotation_by_quaternion(x, q)
        y = point_rotation_by_quaternion(y, q)
        z = point_rotation_by_quaternion(z, q)

        self.vx.set(x)
        self.vy.set(y)
        self.vz.set(z)

        artist = []
        
        for row, line in enumerate(self.lines):
            RealtimePlotter.rolly(line, values[row])
            artist.append(line)
        artist.append(self.vx)
        artist.append(self.vy)
        artist.append(self.vz)

        return artist#self.lines#, self.vx, self.vy, self.vz


