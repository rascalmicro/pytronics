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

import os, serial, subprocess
from time import sleep, time

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
    return names[pin]

def read_analog(pin):
    chan = decode_pin_name(pin) - 96
    command = 'cat /sys/devices/platform/at91_adc/chan' + str(chan)
    reading = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    return reading.communicate()[0].strip() # The [0] selects stdout
                                              # ([1] would access stderr)

def read_pin(pin):
    pin = decode_pin_name(pin)
    command = 'cat /sys/class/gpio/gpio' + str(pin) + '/value'
    state = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    return state.communicate()[0].strip() # The [0] selects stdout
                                          # ([1] would access stderr)

def send_serial(text):
    ser = serial.Serial('/dev/ttyS1', 19200, timeout=1)
    ser.write(str(text[0:80]))
    ser.close()

def set_pin_high(pin):
    pin = decode_pin_name(pin)
    command = 'echo 1 > /sys/class/gpio/gpio' + str(pin) + '/value'
    subprocess.Popen(command, shell=True)

def set_pin_low(pin):
    pin = decode_pin_name(pin)
    command = 'echo 0 > /sys/class/gpio/gpio' + str(pin) + '/value'
    subprocess.Popen(command, shell=True)

def summarize_analog_data():
    import time

# TODO: Figure out how the byte rounding works below to conserve RAM
    filename = '/home/root/ana.log'
    try:
        f = open(filename, 'r')
    except:
        return [[0],[0],[0],[0]]
    if (os.stat(filename).st_size < 10000):
        return [[0],[0],[0],[0]]
    f.seek(-10000, 2) # seek 10000 bytes before the end of the file
    data = f.readlines(100000)[-100:-1] # try to read 100000 bytes
    f.close()
    cur_time = time.time()
    times = [str(float(line.strip().split(',')[0]) - cur_time) for line in data]
    r1 = [line.strip().split(',')[1] for line in data]
    r2 = [line.strip().split(',')[2] for line in data]
    r3 = [line.strip().split(',')[3] for line in data]
    r4 = [line.strip().split(',')[4] for line in data]

    p1 = ['[' + str(t) + ', ' + str(r) + ']' for t, r in zip(times, r1)]
    p2 = ['[' + str(t) + ', ' + str(r) + ']' for t, r in zip(times, r2)]
    p3 = ['[' + str(t) + ', ' + str(r) + ']' for t, r in zip(times, r3)]
    p4 = ['[' + str(t) + ', ' + str(r) + ']' for t, r in zip(times, r4)]

    summary = ('[' + ','.join(p1) + ']', '[' + ','.join(p2) + ']', '[' + ','.join(p3) + ']', '[' + ','.join(p4) + ']')
    return summary

def analogger():
    while(1):
        reading0 = str(float(read_analog(0)) * 3.3 / 1024.0)
        reading1 = str(float(read_analog(1)) * 3.3 / 1024.0)
        reading2 = str(float(read_analog(2)) * 3.3 / 1024.0)
        reading3 = str(float(read_analog(3)) * 3.3 / 1024.0)
        f = open('/home/root/ana.log', 'a')
        f.write(','.join([str(time()), reading0, reading1, reading2, reading3]) + '\n')
        f.close()
        sleep(1)