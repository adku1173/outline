# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 17:11:50 2018

@author: TU-Berlin
"""

from DEDITECIF import *
# bokeh imports 
from bokeh.plotting import figure, curdoc
from bokeh.layouts import gridplot, column, row
from bokeh.models.widgets import Button, TextInput


m = DEDITECIF()
#m.zero_position()
global deg
deg = 2.5

# Buttons
zero_position = Button(label="reset to zero")
forward = Button(label="forward")
backward = Button(label="backward")
#stop_turning = Button(label="stop turning")

# TextInputs
position = TextInput(value=str(0), title="turntable position")
position.disabled = True
deg_step = TextInput(value=str(deg), title="deg step:")

# callbacks
def change_deg_step(attr,old,new):
    global deg
    deg = int(float(new))
deg_step.on_change("value", change_deg_step)

def back():
    global deg
    m.turn_back(deg)
    new_pos_val = float(position.value) - deg
    if new_pos_val <= -360:
        new_pos_val += 360
    position.value = str(new_pos_val)

def forw():
    global deg
    m.turn_forward(deg)
    new_pos_val = float(position.value) + deg
    if new_pos_val <= -360:
        new_pos_val += 360
    position.value = str(new_pos_val)
    
def zero():
    m.zero_position()
    position.value = str(0)

#def stop():
#    m.SetAllOutputs(0)
#    position.value = str(-1) # indicates error

forward.on_click(forw)
backward.on_click(back)
zero_position.on_click(zero)
#stop_turning.on_click(stop)


################################## setup document #############################

# set up Bokeh Document
r = row(backward,zero_position, forward)
c = column(position,deg_step)
fig_all = gridplot([[r,c]])
curdoc().add_root(fig_all)


