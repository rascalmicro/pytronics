#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2011 Rascal Micro LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but without any warranty; without even the implied warranty of
# merchantability or fitness for a particular purpose. See the full
# text of the GNU General Public License at 
# <http://www.gnu.org/licenses/gpl.txt> for the details.

# Listing of /sys/class/gpio
# export      gpio107     gpio66      gpio69      gpio72      gpio97      gpiochip32  unexport
# gpio100     gpio64      gpio67      gpio70      gpio73      gpio98      gpiochip64

def decode_pin_name(pin):
    names = {
        'LED': 107, # PC11
        '0': 69, # PB5
        '1': 68, # PB4
        '2': 71, # PB7
        '3': 70, # PB6
        '4': 73, # PB9
        '5': 72, # PB8
        '6': 55, # PA23
        '7': 56, # PA24
        '8': 100, # PC4
        '9': 101, # PC5
        '10': 67, # PB3
        '11': 65, # PB1
        '12': 64, # PB0
        '13': 66, # PB2
        'A0': 96, # PC0
        'A1': 97, # PC1
        'A2': 98, # PC2
        'A3': 99, # PC3
    }
    try:
        return names[str(pin)]
    except KeyError as bad_name:
        print("There's no pin called {0}. Try a pin 3-13, 'LED', or 'A0'-'A3'.".format(bad_name)) 

def analogRead(pin):
    chan = decode_pin_name(pin) - 96 # offset of 96 maps channel to Port C on CPU
    if(chan in range(4)):
        with open('/sys/devices/platform/at91_adc/chan' + str(chan), 'r') as f:
            reading = f.read()
        return reading.strip()
    else:
        return "Not an analog pin. Try 'A0', 'A1', 'A2', or 'A3'."

def analogWrite():
    pass

# Reads a value from a specified digital pin
# Returns '0' or '1'
def digitalRead(pin):
    pin = decode_pin_name(pin)
    with open('/sys/class/gpio/gpio' + str(pin) + '/value', 'r') as f:
        reading = f.read()
    return reading.strip()

# Write a HIGH or LOW value to a digital pin
# E.g. digitalWrite('11', 'HIGH')
def digitalWrite(pin, state):
    pin = decode_pin_name(pin)
    with open('/sys/class/gpio/gpio' + str(pin) + '/value', 'w') as f:
        if (state == 'HIGH'):
            f.write('1')
        else:
            f.write('0')

# Configures the specified pin to behave either as an input or an output
# E.g. pinMode('5', 'INPUT')
def pinMode(pin, mode):
    pin = decode_pin_name(pin)
    with open('/sys/class/gpio/gpio' + str(pin) + '/direction', 'w') as f:
        if (mode == 'INPUT'):
            f.write('in')
        else:
            f.write('out')

# Called with list of pins e.g. [ 'LED' ]
# Returns dictionary of tuples { 'pin': (direction, value) }
def readPins(pinlist):
    pins = {}
    for pin in pinlist:
        syspin = str(decode_pin_name(pin))
        try:
            with open('/sys/class/gpio/gpio' + syspin + '/direction', 'r') as f:
                direction = f.read().strip()
            with open('/sys/class/gpio/gpio' + syspin + '/value', 'r') as f:
                value = f.read()
            pins[pin] = (direction.strip(), value.strip())
        except:
            print ('## readPins ## Cannot access pin {0} ({1})'.format(pin, syspin))
    return pins

def i2cRead(addr, reg = 0, size = 'B', length = 0):
    from i2c import _i2cRead
    return _i2cRead(addr, reg, size, length)

def i2cWrite(addr, reg, val = '', size = 'B'):
    from i2c import _i2cWrite
    _i2cWrite(addr, reg, val, size)

def serialRead():
    pass

def serialWrite(text, speed=19200, port='1'):
    import serial
    ports = {
        '1': '/dev/ttyS1',
        '2': '/dev/ttyS2',
        '3': '/dev/ttyS3'
    }
    ser = serial.Serial(ports[str(port)], speed, timeout=1)
    ser.write(str(text[0:80]))
    ser.close()
    
def toggle(pin):
    if digitalRead(pin):
        digitalWrite(pin, 'LOW')
    else:
        digitalWrite(pin, 'HIGH')

def spiRead():
    pass

def spiWrite(val):
    pass