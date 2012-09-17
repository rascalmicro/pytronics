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
    args = i2c_smbus_ioctl_data(read_write, command, size, data)
    return fcntl.ioctl(file, I2C_SMBUS, args)

def i2c_smbus_write_quick(file, mode):
    if debug: print '## i2c_smbus_write_quick ##: mode 0x{0:02X}'.format(mode)
    data = i2c_smbus_data(0)
    i2c_smbus_access(file, mode, 0, I2C_SMBUS_QUICK, pointer(data))

def i2c_smbus_read_byte(file):
    if debug: print '## i2c_smbus_read_byte ##'
    data = i2c_smbus_data(0)
    i2c_smbus_access(file, I2C_SMBUS_READ, 0, I2C_SMBUS_BYTE, pointer(data))
    return 0x0FF & data.byte

def i2c_smbus_write_byte(file, daddr):
    if debug: print '## i2c_smbus_write_byte ##: daddr 0x{0:02X}'.format(daddr)
    data = i2c_smbus_data(0)
    i2c_smbus_access(file, I2C_SMBUS_WRITE, daddr, I2C_SMBUS_BYTE, pointer(data))

def i2c_smbus_read_byte_data(file, daddr):
    if debug: print '## i2c_smbus_read_byte_data ##: daddr 0x{0:02X}'.format(daddr)
    data = i2c_smbus_data(0)
    i2c_smbus_access(file, I2C_SMBUS_READ, daddr, I2C_SMBUS_BYTE_DATA, pointer(data))
    return 0x0FF & data.byte

def i2c_smbus_write_byte_data(file, daddr, value):
    if debug: print '## i2c_smbus_write_byte_data ##: daddr 0x{0:02X}, value=0x{1:02X}'.format(daddr, value)
    data = i2c_smbus_data(0)
    data.byte = value
    i2c_smbus_access(file, I2C_SMBUS_WRITE, daddr, I2C_SMBUS_BYTE_DATA, pointer(data))

def i2c_smbus_read_word_data(file, daddr):
    if debug: print '## i2c_smbus_read_word_data ##: daddr 0x{0:02X}'.format(daddr)
    data = i2c_smbus_data(0)
    i2c_smbus_access(file, I2C_SMBUS_READ, daddr, I2C_SMBUS_WORD_DATA, pointer(data))
    return 0x0FFFF & data.word

def i2c_smbus_write_word_data(file, daddr, value):
    if debug: print '## i2c_smbus_write_word_data ##: daddr 0x{0:02X}, value=0x{1:04X}'.format(daddr, value)
    data = i2c_smbus_data(0)
    data.word = value
    i2c_smbus_access(file, I2C_SMBUS_WRITE, daddr, I2C_SMBUS_WORD_DATA, pointer(data))

def i2c_smbus_read_i2c_block_data(file, daddr, length):
    if debug: print '## i2c_smbus_read_i2c_block_data ##: daddr 0x{0:02X}, length 0x{1:02X}'.format(daddr, length)
    data = i2c_smbus_data(0)
    if length > 32:
        length = 32
    data.block[0] = length
    i2c_smbus_access(file, I2C_SMBUS_READ, daddr,
            I2C_SMBUS_I2C_BLOCK_BROKEN if length == 32 else I2C_SMBUS_I2C_BLOCK_DATA, pointer(data))
    values = []
    for i in range(data.block[0]):
        values.append(data.block[i + 1])
    return values

def i2c_smbus_write_i2c_block_data(file, daddr, length, values):
    if debug: print '## i2c_smbus_write_i2c_block_data ##: daddr 0x{0:02X}, length 0x{1:02X}'.format(daddr, length)
    data = i2c_smbus_data(0)
    if length > 32:
        length = 32
    data.block[0] = length
    for i in range(length):
        data.block[i + 1] = values[i]
    i2c_smbus_access(file, I2C_SMBUS_WRITE, daddr, I2C_SMBUS_I2C_BLOCK_BROKEN, pointer(data))

# Main entry points
def _i2cRead(addr, reg = 0, size = '', length = 0):
    if debug: print '## i2cRead ## addr={0}, reg={1}, size={2}, length={3}'.format(addr, reg, size, length)
    file = os.open(RASCAL_I2C, os.O_RDWR)
    fcntl.ioctl(file, I2C_SLAVE, addr)
    if size.upper() == 'I' and length > 0:
        data = i2c_smbus_read_i2c_block_data(file, reg, length)
    elif size.upper() == 'W':
        data = i2c_smbus_read_word_data(file, reg)
    elif size.upper() == 'B':
        data = i2c_smbus_read_byte_data(file, reg)
    else:
        data = i2c_smbus_read_byte(file)
    os.close(file)
    return data

def _i2cWrite(addr, reg, value = '', size = 'B'):
    if value == '': size = 'C'; value = 0
    if debug: print '## i2cWrite ## addr=0x{0:02x}, reg=0x{1:02x}, value=0x{2:04X}, size={3}'.format(addr, reg, value, size)
    file = os.open(RASCAL_I2C, os.O_RDWR)
    fcntl.ioctl(file, I2C_SLAVE, addr)
    if size.upper() == 'I' and isinstance(value, list) and len(value) > 0:
        data = i2c_smbus_write_i2c_block_data(file, reg, len(value), value)
    elif size.upper() == 'W':
        data = i2c_smbus_write_word_data(file, reg, value)
    elif size.upper() == 'B':
        data = i2c_smbus_write_byte_data(file, reg, value)
    else:
        data = i2c_smbus_write_byte(file, reg)
    os.close(file)
    return data

# Support for scanning i2C bus
def probe_bus(file, addr):
    # Set slave address
    try:
        fcntl.ioctl(file, I2C_SLAVE, addr)
        try:
            if ((addr >= 0x30 and addr <= 0x37) or (addr >= 0x50 and addr <= 0x5F)):
                res = i2c_smbus_read_byte(file)
            else:
                res = i2c_smbus_write_quick(file, I2C_SMBUS_WRITE)
            return addr
        except IOError:
            return I2C_SCAN_NODEV
        except Exception as e:
            print '## probe_bus ## Unexpected exception: probe address {0}'.format(e)
    except IOError:
        return I2C_SCAN_BUSY
    except Exception as e:
        print '## probe_bus ## Unexpected exception: set slave address {0}'.format(e)
        
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
