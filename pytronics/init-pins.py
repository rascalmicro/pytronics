#!/usr/bin/python

import os.path
from pins import NAMES

for name in NAMES:
    with open('/sys/class/gpio/export', 'w') as f:
        gpio_num = NAMES[name]
        if os.path.exists('/sys/devices/virtual/gpio/gpio{0}'.format(gpio_num)):
            print 'gpio{0} already exported'.format(gpio_num)
        else:
            f.write(gpio_num)
            print('Exported gpio{0}'.format(gpio_num))

