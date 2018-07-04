# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 12:27:38 2018

@author: TU-Berlin
"""

from ctypes import *
import time

class DEDITECIF(object):
    """
    This class maps the DEDITEC driver to Python.
    
    ----------------------------------------------------
    DEDITEC Pin assignment of D-SUB-9 connector:
        
        Pin - ttlchannel
        ----------------
        1   - GND
        5   - 0
        9   - 1
        4   - 2
        8   - 3
        3   - 4
        7   - 5
        2   - 6
        6   - 7
        
    ----------------------------------------------------
    Outline ET2/ST2 Turntable Pin assignment of D-SUB-9:
        
        Pin - control protocol
        ----------------------
        1   - unit A movement ahead bit (write bit)
        2   - unit B movement ahead bit (write bit)
        3   - unit A movement behind bit (write bit)
        4   - unit B movement behind bit (write bit)
        5   - GND
        6   - unit A step bit (reading bit)
        7   - unit B step bit (reading bit)
        8   - unit A zero position bit (reading bit)
        9   - unit B zero position bit (reading bit)
        
    
    ----------------------------------------------------
    Due to the fact that physical GND Pins of both connectors are not the same,
    connector which maps physical pins is needed. 

    At the moment the following mapping is applied to the connector:
        
        Pin DEDITEC - Pin Outline ET2 
        -----------------------------
        1 (GND)     - 5 (GND)
        3 (TTL4)    - 3 (unit A movement behind bit)
        6 (TTL7)    - 6 (unit A step bit (reading bit))
        8 (TTL3)    - 8 (unit A zero position bit (reading bit))  
        9 (TTL1)    - 1 (unit A movement ahead bit)                   

    other pins are not connected. Unit B is neglected.

    Note:
    ----
    If mapping is changed -> need to applied at constants in __init__ function
    """
    
    def __init__(self):
        """
        Note:
        -----
        Driver holds more functions -> just initialize most important
        """

        # access dll via ctypes
        delib = windll.delib64
          
        #open module functionality
        self.libOpenModule = delib.DapiOpenModule 
        self.libOpenModule.argtypes = [c_ulong, c_ulong] 
        #returns installed DELIB version
        self.libGetDELIBVersion = delib.DapiGetDELIBVersion 
        # close module functionality
        self.libCloseModule = delib.DapiCloseModule
        self.libCloseModule.argtypes = [c_ulong]
        # set output pin functionality
        self.libDOSet1 = delib.DapiDOSet1
        self.libDOSet1.argtypes = [c_ulong,c_ulong,c_ulong] 
        self.libDOSet8 = delib.DapiDOSet8
        self.libDOSet8.argtypes = [c_ulong,c_ulong,c_ulong] 
        # get pin status functionality
        self.libDIGet1 = delib.DapiDIGet1
        self.libDIGet1.argtypes = [c_ulong,c_ulong] 
        # sets the direction of 8 consecutive TTL-in/Outputs (1-bit-wise)
        self.libSpecialCommand = delib.DapiSpecialCommand 

        self.libPing = delib.DapiPing
        
        # Set turntable mapping constants 
        self.foreward_unitA = 1 # ttl 1 
        self.backward_unitA = 4 # ttl 4
        self.step_bit_unitA = 7 # ttl 7 
        self.zero_position_bit_unitA = 3 # ttl 3 

        # DEDITEC constants
        self.moduleID = 9 # moduleID can be figured out from delib.h file 
        self.channel = 0 # channel for certain module can be configured via configuration tool
        self.DAPI_SPECIAL_CMD_SET_DIR_DX_1 = 0x03 # can be figured out from delib.h file
        self.DAPI_SPECIAL_CMD_GET_MODULE_CONFIG	= 0x01 # can be figured out from delib.h file
        self.DAPI_SPECIAL_GET_MODULE_CONFIG_PAR_DI = 1 # can be figured out from delib.h file
        self.DAPI_SPECIAL_GET_MODULE_CONFIG_PAR_DO = 2 # can be figured out from delib.h file

        # open module 
        self.handle = self.libOpenModule(self.moduleID,self.channel) # need to open module for device access

        if self.handle == 0: # 
            print("Opening Module Error!")        

#    def OpenModule(self):
#        """ Returns handle of module """        
#        return self.libOpenModule(self.moduleID,self.channel)

#    def Ping(self):
#        """ returns 1 if ok """
#        return self.libPing(self.handle,1)

    #: function returns installed DELIB version
    def GetDELIBVersion(self):
        """
        Returns
        -------
        int with DELIB version
        """        
        return self.libGetDELIBVersion(0,0) # args need to be zero

    #: function closes opened module
    def CloseModule(self):
        """ 
        Returns
        -------
        None
        """
        self.libCloseModule(self.handle)

    #: command set a single output
    def SetValue(self,ttlchannel,value):
        """ 
        set a desired pin on (1) or off (0)
        
        Parameters
        ----------
        ttlchannel: int or hex
            specifies the ttlchannel which should be set on or off
        value: int (1 or 0)
            1: set channel on, 0: set channel off
            
        Returns
        -------
        None
        """
        self.libDOSet1(self.handle,ttlchannel,value)

    #: reads a single digital input
    def GetValue(self,ttlchannel):
        """ 
        reads a single digital input
        
        Parameters
        ----------
        ttlchannel: int or hex
            specifies the ttlchannel to read
            
        Returns
        -------
        State of the input (1 or 0)
        """
        return self.libDIGet1(self.handle,ttlchannel)

    # sets all 8 digital outputs to values
    def SetAllOutputs(self,value):
        """ 
        sets all 8 digital outputs to on (1) or off (0)
        
        Parameters
        ----------
        value: int (1 or 0)
            1: set channels on, 0: set channels off
            
        Returns
        -------
        None
        """
        self.libDOSet8(self.handle,0,value)

    #: sets direction of TTL- In/Outputs (1-bit-wise) 
    def SetPinIO(self, ttlchannel):
        """ 
        set a desired ttchannel to output, others to input
        
        Parameters
        ----------
        ttlchannel: int 
            specifies the ttlchannel which should be set as output
            
        Returns
        -------
        None
        
        Note:
        ----
        libSpecialCommand,
        takes hex number as input for TTL channel with following mapping:
        """
        ttltohex = {'0':0x01, # maps ttl channel to hex value
                    '1':0x02,
                    '2':0x04,
                    '3':0x08,
                    '4':0x10,
                    '5':0x20,
                    '6':0x40,
                    '7':0x80}
    
        ch = ttltohex[str(ttlchannel)] # map ttl channel to hex value
        return self.libSpecialCommand(self.handle,self.DAPI_SPECIAL_CMD_SET_DIR_DX_1, 0, ch, 0)
        

    #: returns number of digital inputs 
    def GetNumDigitalInputs(self):
        """ 
        Returns
        -------
        number of digital inputs as type int
        (always '8' for USB-MINI-TTL-8)
        """
        return self.libSpecialCommand(self.handle,
                                      self.DAPI_SPECIAL_CMD_GET_MODULE_CONFIG,
                                      self.DAPI_SPECIAL_GET_MODULE_CONFIG_PAR_DI,
                                      0,0)

    #: returns number of digital outputs 
    def GetNumDigitalOutputs(self):
        """ 
        Returns
        -------
        number of digital outputs as type int 
        (always '8' for USB-MINI-TTL-8)
        """
        return self.libSpecialCommand(self.handle,
                                      self.DAPI_SPECIAL_CMD_GET_MODULE_CONFIG,
                                      self.DAPI_SPECIAL_GET_MODULE_CONFIG_PAR_DO,
                                      0,0)        


##### functions for turntable access #####

    #: rotate turntable backwards
    def turn_back(self,deg=2.5):
        """ 
        rotate turntable backwards 
        
        Parameters
        ----------
        deg: float or int (need to be a multiple of 2.5)
            specifies how many degrees to rotate
            minimum allowed value is 2.5
            
        Returns
        -------
        None
        """

        numpulse = int(deg/2.5) # how many pulses to read till deg limit is reached

        self.SetPinIO(self.backward_unitA) # set pin to output others to inputs        
        self.SetValue(self.backward_unitA,1) # set Pin value to 1 
        time.sleep(0.3) # wait for flank
        i = 0 # pulse count
        while True:
            if self.GetValue(self.step_bit_unitA) > 0: # read status of position bit 
                pass
            else:            
                i += 1 # increase pulse count
                if i == numpulse: # if enough pulses count
                    self.SetValue(self.backward_unitA,0) # stop turning
                    break
                else:
                    time.sleep(0.3) # wait for next pulse

    #: rotate turntable forward
    def turn_forward(self,deg=2.5):
        """ 
        rotate turntable forward 
        
        Parameters
        ----------
        deg: float or int (need to be a multiple of 2.5)
            specifies how many degrees to rotate
            minimum allowed value is 2.5
            
        Returns
        -------
        None
        """

        numpulse = int(deg/2.5) # how many pulses for desired degree

        self.SetPinIO(self.foreward_unitA) # set to output others to inputs        
        self.SetValue(self.foreward_unitA,1)
        time.sleep(0.3)
        i = 0 # pulse count
        while True:
            if self.GetValue(self.step_bit_unitA) > 0:
                pass
            else:
                i += 1
                if i == numpulse:
                    self.SetValue(self.foreward_unitA,0)
                    break
                else:
                    time.sleep(0.3)                    

    # turn turntable to zero position
    def zero_position(self):        
        """
        zeros turntable position
        
        Returns
        -------
        None
        """
        self.SetPinIO(self.backward_unitA) # set to output others to inputs     
        self.SetValue(self.backward_unitA,1) # turn in backward direction
        while self.GetValue(self.zero_position_bit_unitA) > 0: # 
            pass
        else: # stop 
            self.SetValue(self.backward_unitA,0) 
            
#
if __name__ == '__main__':
    from DEDITECIF import *

    m = DEDITECIF()

    # show delib version
    print('delib version is:', m.GetDELIBVersion())
    
    print('number digital inputs:', m.GetNumDigitalInputs())
    
    print('number digital outputs:', m.GetNumDigitalOutputs())

    time.sleep(1)

#   turn forward 10 deg
    print("turn 10 degree forward...")
    m.turn_forward(deg=10)
#
    time.sleep(2)
#
    print("turn to zero position...")
    m.zero_position()
    
    # if turntable does not stop turning -> reset: 
    m.SetAllOutputs(0) #set all outputs to zero


        
        
    

        
    
