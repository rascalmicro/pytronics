import os, fcntl
from ctypes import *

RASCAL_I2C = '/dev/i2c-0'

# smbus_access read or write markers
I2C_SMBUS_READ = 1
I2C_SMBUS_WRITE = 0

# SMBus transaction types (size parameter in the above functions) 
I2C_SMBUS_QUICK = 0
I2C_SMBUS_BYTE = 1
I2C_SMBUS_BYTE_DATA = 2 
I2C_SMBUS_WORD_DATA= 3
I2C_SMBUS_PROC_CALL = 4
I2C_SMBUS_BLOCK_DATA = 5
I2C_SMBUS_I2C_BLOCK_BROKEN = 6
I2C_SMBUS_BLOCK_PROC_CALL = 7       # SMBus 2.0
I2C_SMBUS_I2C_BLOCK_DATA = 8

I2C_SLAVE = 0x0703
I2C_FUNCS = 0x0705
I2C_SMBUS = 0x0720      # SMBus-level access

I2C_SCAN_BUSY = -2
I2C_SCAN_NODEV = -1
I2C_SCAN_SKIPPED = 0

# Data for SMBus Messages 
I2C_SMBUS_BLOCK_MAX = 32        # As specified in SMBus standard
I2C_SMBUS_I2C_BLOCK_MAX	= 32    # Not specified but we use same structure

debug = False

class i2c_smbus_data(Union):
    _fields_ = [('byte', c_ubyte),
                ('word', c_uint),
                ('block', c_ubyte * 34)]

class i2c_smbus_ioctl_data(Structure):
    _fields_ = [('read_write', c_ubyte),
                ('command', c_ubyte),
                ('size', c_int),
                ('data', POINTER(i2c_smbus_data))]

def i2c_smbus_access(file, read_write, command, size, data):
    try:
        args = i2c_smbus_ioctl_data(read_write, command, size, data)
        return fcntl.ioctl(file, I2C_SMBUS, args)
    except IOError, e:
        if debug: print '## i2c_smbus_access ##: IOError {0}'.format(e)
        return -1
    except IOError, e:
        return -1
    except Exception, e:
        print '## i2c_smbus_access ## {0}'.format(e)
        return -1

def i2c_smbus_write_quick(file, value):
    data = i2c_smbus_data(0)
    return i2c_smbus_access(file, value, 0, I2C_SMBUS_QUICK, pointer(data))

def i2c_smbus_read_byte(file):
    if debug: print '## i2c_smbus_read_byte ##'
    data = i2c_smbus_data(0)
    if (i2c_smbus_access(file, I2C_SMBUS_READ, 0, I2C_SMBUS_BYTE, pointer(data)) == 0):
        return 0x0FF & data.byte
    else:
        return -1

def i2c_smbus_write_byte(file, value):
    if debug: print '## i2c_smbus_write_byte ##: value 0x{0:00X}'.format(value)
    data = i2c_smbus_data(0)
    return i2c_smbus_access(file, I2C_SMBUS_WRITE, value, I2C_SMBUS_BYTE, pointer(data))

def i2c_smbus_read_byte_data(file, daddr):
    if debug: print '## i2c_smbus_read_byte_data ##: daddr {0}'.format(daddr)
    data = i2c_smbus_data(0)
    if (i2c_smbus_access(file, I2C_SMBUS_READ, daddr, I2C_SMBUS_BYTE_DATA, pointer(data)) == 0):
        return 0x0FF & data.byte
    else:
        return -1

def i2c_smbus_write_byte_data(file, daddr, value):
    if debug: print '## i2c_smbus_write_byte_data ##: daddr {0}, value=0x{1:00X}'.format(daddr, value)
    data = i2c_smbus_data(0)
    data.byte = value
    return i2c_smbus_access(file, I2C_SMBUS_WRITE, daddr, I2C_SMBUS_BYTE_DATA, pointer(data))

def i2c_smbus_read_word_data(file, daddr):
    if debug: print '## i2c_smbus_read_word_data ##: daddr {0}'.format(daddr)
    data = i2c_smbus_data(0)
    if (i2c_smbus_access(file, I2C_SMBUS_READ, daddr, I2C_SMBUS_WORD_DATA, pointer(data)) == 0):
        return 0x0FFFF & data.word
    else:
        return -1

def i2c_smbus_write_word_data(file, daddr, value):
    if debug: print '## i2c_smbus_write_word_data ##: daddr {0}, value=0x{1:0000X}'.format(daddr, value)
    data = i2c_smbus_data(0)
    data.word = value
    return i2c_smbus_access(file, I2C_SMBUS_WRITE, daddr, I2C_SMBUS_WORD_DATA, pointer(data))

# Main entry points
def _i2cRead(addr, reg = 0, size = ''):
    if debug: print '## i2cRead ## addr={0}, reg={1}, size={2}'.format(addr, reg, size)
    try:
        file = os.open(RASCAL_I2C, os.O_RDWR)
        try:
            fcntl.ioctl(file, I2C_SLAVE, addr)
            if size.upper() == 'W':
                data = i2c_smbus_read_word_data(file, reg)
            elif size.upper() == 'B':
                data = i2c_smbus_read_byte_data(file, reg)
            else:
                data = i2c_smbus_read_byte(file)
        except Exception, e:
            if debug: print '## i2cRead ## Can\'t set slave addr {0}'.format(e)
            data = -1
        os.close(file)
    except OSError:
        if debug: print '## i2cRead ## Can\'t open {0}'.format(RASCAL_I2C)
        data = -2
    return data

def _i2cWrite(addr, reg, value, size):
    if debug: print '## i2cWrite ## addr=0x{0:02x}, reg=0x{1:02x}, value=0x{2:04X}, size={3}'.format(addr, reg, value, size)
    try:
        file = os.open(RASCAL_I2C, os.O_RDWR)
        try:
            fcntl.ioctl(file, I2C_SLAVE, addr)
            if size.upper() == 'W':
                data = i2c_smbus_write_word_data(file, reg, value)
            elif size.upper() == 'B':
                data = i2c_smbus_write_byte_data(file, reg, value)
            else:
                data = i2c_smbus_write_byte(file, value)
        except Exception, e:
            if debug: print '## i2cWrite ## Can\'t set slave addr {0}'.format(e)
            data = -1
        os.close(file)
    except OSError:
        if debug: print '## i2cWrite ## Can\'t open {0}'.format(RASCAL_I2C)
        data = -2
    return data

# Support for scanning i2C bus
def probe_bus(file, addr):
    # Set slave address
    try:
        fcntl.ioctl(file, I2C_SLAVE, addr)
        if ((addr >= 0x30 and addr <= 0x37) or (addr >= 0x50 and addr <= 0x5F)):
            res = i2c_smbus_read_byte(file)
        else:
            res = i2c_smbus_write_quick(file, I2C_SMBUS_WRITE)
        if res < 0:
            return I2C_SCAN_NODEV
        else:
            return addr
    except Exception, e:
        return I2C_SCAN_BUSY
    
# Address status: 0=out of range, -1=not present, -2=busy, otherwise device address
def scanBus(first = 0x03, last = 0x77):
    file = os.open(RASCAL_I2C, os.O_RDWR)
    scan = {}
    for i in range(0, 128, 16):
        row = ()
        for j in range(0, 16):
            addr = i + j
            # Skip unwanted addresses
            if (addr < first) or (addr > last):
                row += (I2C_SCAN_SKIPPED,)
            else:
                row += (probe_bus(file, addr),)
        scan[i] = row
    os.close(file)
    return scan



