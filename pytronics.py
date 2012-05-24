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

def digitalRead(pin):
    pin = decode_pin_name(pin)
    with open('/sys/class/gpio/gpio' + str(pin) + '/value', 'r') as f:
        reading = f.read()
    return reading.strip()

def digitalWrite(pin, state):
    pin = decode_pin_name(pin)
    with open('/sys/class/gpio/gpio' + str(pin) + '/value', 'w') as f:
        if (state == 'HIGH'):
            f.write('1')
        else:
            f.write('0')

def i2cRead():
    pass

def i2cWrite(val):
    cmd = 'i2cset -y 0 0x29 ' + str(val)
    subprocess.Popen([cmd], shell=True)

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